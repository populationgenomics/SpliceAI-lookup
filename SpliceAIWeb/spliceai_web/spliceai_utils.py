from pkg_resources import resource_filename
import pandas as pd
import numpy as np
import re
from pyfaidx import Fasta
from keras.models import load_model
from keras import backend as K
import logging

def one_hot_encode(seq):

    map = np.asarray([[0, 0, 0, 0],
                      [1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])

    seq = seq.upper().replace('A', '\x01').replace('C', '\x02')
    seq = seq.replace('G', '\x03').replace('T', '\x04').replace('N', '\x00')

    return map[np.fromstring(seq, np.int8) % 5]


def normalise_chrom(source, target):

    def has_prefix(x):
        return x.startswith('chr')

    if has_prefix(source) and not has_prefix(target):
        return source.strip('chr')
    elif not has_prefix(source) and has_prefix(target):
        return 'chr'+source

    return source

def get_delta_scores(record, ann, dist_var, mask):

    cov = 2*dist_var+1
    wid = 10000+cov
    delta_scores = []
    spliceai_variant_records = []

    try:
        record.chrom, record.pos, record.ref, len(record.alts)
    except TypeError:
        logging.warning('Skipping record (bad input): {}'.format(record))
        return delta_scores

    (genes, strands, idxs) = ann.get_name_and_strand(record.chrom, record.pos)
    if len(idxs) == 0:
        return delta_scores

    chrom = normalise_chrom(record.chrom, list(ann.ref_fasta.keys())[0])
    try:
        seq = ann.ref_fasta[chrom][record.pos-wid//2-1:record.pos+wid//2].seq
    except (IndexError, ValueError):
        logging.warning('Skipping record (fasta issue): {}'.format(record))
        return delta_scores

    if seq[wid//2:wid//2+len(record.ref)].upper() != record.ref:
        logging.warning('Skipping record (ref issue): {}'.format(record))
        return delta_scores

    if len(seq) != wid:
        logging.warning('Skipping record (near chromosome end): {}'.format(record))
        return delta_scores

    if len(record.ref) > 2*dist_var:
        logging.warning('Skipping record (ref too long): {}'.format(record))
        return delta_scores

    spliceai_stats = []

    for j in range(len(record.alts)):
        for i in range(len(idxs)):

            if '.' in record.alts[j] or '-' in record.alts[j] or '*' in record.alts[j]:
                continue

            if '<' in record.alts[j] or '>' in record.alts[j]:
                continue

            if len(record.ref) > 1 and len(record.alts[j]) > 1:
                delta_scores.append("{}|{}|.|.|.|.|.|.|.|.".format(record.alts[j], genes[i]))
                continue

            dist_ann = ann.get_pos_data(idxs[i], record.pos)
            pad_size = [max(wid//2+dist_ann[0], 0), max(wid//2-dist_ann[1], 0)]
            ref_len = len(record.ref)
            alt_len = len(record.alts[j])
            del_len = max(ref_len-alt_len, 0)

            x_ref = 'N'*pad_size[0]+seq[pad_size[0]:wid-pad_size[1]]+'N'*pad_size[1]
            x_alt = x_ref[:wid//2]+str(record.alts[j])+x_ref[wid//2+ref_len:]

            x_ref = one_hot_encode(x_ref)[None, :]
            x_alt = one_hot_encode(x_alt)[None, :]

            if strands[i] == '-':
                x_ref = x_ref[:, ::-1, ::-1]
                x_alt = x_alt[:, ::-1, ::-1]

            y_ref = np.mean([ann.models[m].predict(x_ref) for m in range(5)], axis=0)
            y_alt = np.mean([ann.models[m].predict(x_alt) for m in range(5)], axis=0)

            if strands[i] == '-':
                y_ref = y_ref[:, ::-1]
                y_alt = y_alt[:, ::-1]

            if ref_len > 1 and alt_len == 1:
                y_alt = np.concatenate([
                    y_alt[:, :cov//2+alt_len],
                    np.zeros((1, del_len, 3)),
                    y_alt[:, cov//2+alt_len:]],
                    axis=1)
            elif ref_len == 1 and alt_len > 1:
                y_alt = np.concatenate([
                    y_alt[:, :cov//2],
                    np.max(y_alt[:, cov//2:cov//2+alt_len], axis=1)[:, None, :],
                    y_alt[:, cov//2+alt_len:]],
                    axis=1)

            y = np.concatenate([y_ref, y_alt])

            idx_pa = (y[1, :, 1]-y[0, :, 1]).argmax()
            idx_na = (y[0, :, 1]-y[1, :, 1]).argmax()
            idx_pd = (y[1, :, 2]-y[0, :, 2]).argmax()
            idx_nd = (y[0, :, 2]-y[1, :, 2]).argmax()

            mask_pa = np.logical_and((idx_pa-cov//2 == dist_ann[2]), mask)
            mask_na = np.logical_and((idx_na-cov//2 != dist_ann[2]), mask)
            mask_pd = np.logical_and((idx_pd-cov//2 == dist_ann[2]), mask)
            mask_nd = np.logical_and((idx_nd-cov//2 != dist_ann[2]), mask)

            delta_scores.append("{}|{}|{:.2f}|{:.2f}|{:.2f}|{:.2f}|{}|{}|{}|{}|{:.2f}|{:.2f}|{:.2f}|{:.2f}|{:.2f}|{:.2f}|{:.2f}|{:.2f}".format(
                                record.alts[j],
                                genes[i],
                                (y[1, idx_pa, 1]-y[0, idx_pa, 1])*(1-mask_pa),
                                (y[0, idx_na, 1]-y[1, idx_na, 1])*(1-mask_na),
                                (y[1, idx_pd, 2]-y[0, idx_pd, 2])*(1-mask_pd),
                                (y[0, idx_nd, 2]-y[1, idx_nd, 2])*(1-mask_nd),
                                idx_pa-cov//2,
                                idx_na-cov//2,
                                idx_pd-cov//2,
                                idx_nd-cov//2,
                                y[0, idx_pa, 1],
                                y[1, idx_pa, 1],
                                y[0, idx_na, 1],
                                y[1, idx_na, 1],
                                y[0, idx_pd, 2],
                                y[1, idx_pd, 2],
                                y[0, idx_nd, 2],
                                y[1, idx_nd, 2]))

            dist_from_variant = np.arange(-1 * dist_var, 0).tolist()
            dist_from_variant.extend(np.arange(0, dist_var + 1).tolist())

            donor = (y_alt[0, :, 2] - y_ref[0, :, 2]).tolist()
            donor_ref = y_ref[0, :, 2].tolist()
            donor_alt = y_alt[0, :, 2].tolist()
            acceptor = (y_alt[0, :, 1] - y_ref[0, :, 1]).tolist()
            acceptor_ref = y_ref[0, :, 1].tolist()
            acceptor_alt = y_alt[0, :, 1].tolist()

            spliceai_variant_record = {}
            spliceai_stats = []

            for index in np.arange(0, len(dist_from_variant)):
                stat_record = {
                    'dist_from_variant': dist_from_variant[index],
                    'donor_ref': donor_ref[index],
                    'donor_alt': donor_alt[index],
                    'donor': donor[index],
                    'acceptor_ref': acceptor_ref[index],
                    'acceptor_alt': acceptor_alt[index],
                    'acceptor': acceptor[index]
                }

                spliceai_stats.append(stat_record)

            spliceai_variant_record['gene'] = genes[i]
            spliceai_variant_record['strand'] = strands[i]
            spliceai_variant_record['chr'] = record.chrom
            spliceai_variant_record['pos'] = record.pos
            spliceai_variant_record['ref'] = record.ref
            spliceai_variant_record['alt'] = record.alts[j]
            spliceai_variant_record['stats'] = spliceai_stats

            spliceai_variant_records.append(spliceai_variant_record)

    K.clear_session()

    return spliceai_variant_records