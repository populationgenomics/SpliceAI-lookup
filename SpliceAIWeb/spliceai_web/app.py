import os
import json
import logging

from .spliceai_utils import get_delta_scores
from spliceai.utils import Annotator
from flask import request
from flask import Flask
from flask_cors import CORS

logger = logging.getLogger(__name__)

FORMAT = "%(asctime)s - %(name)-20s [%(funcName)-20s] %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {'origins': "*"}})

app.config['HG19'] = os.getenv("HG19")
app.config['HG38'] = os.getenv("HG38") #'/Users/himanshujoshi/Projects/hg_ref/b37/human_g1k_v37.fasta'

class Record:
    chrom: str = None
    pos: int = None
    ref: str = None
    alts: list() = None

@app.route('/spliceai/api/get_variant_assessment', methods=['POST'])
def get_variant_assessment():
    logger.debug("Invoking get_variant_assessment")
    logger.debug("Chromosome: " + request.form['chrom'])
    logger.debug("Position: " + request.form['pos'])
    logger.debug("Ref: " + request.form['ref'])
    logger.debug("Alt: " + request.form['alt'])
    logger.debug("Assembly: " + request.form['assembly'])
    logger.debug("Distance: " + request.form['distance'])
    logger.debug("Mask: " + request.form['mask'])

    Record.chrom = request.form['chrom']
    Record.pos = int(request.form['pos'])
    Record.ref = request.form['ref']
    Record.alts = [request.form['alt']]
    
    assembly = request.form['assembly']
    distance = int(request.form['distance'])
    mask = int(request.form['mask'])

    ann = Annotator(app.config['HG19'], assembly)

    pred = get_delta_scores(Record, ann, distance, mask)

    return json.dumps(pred)