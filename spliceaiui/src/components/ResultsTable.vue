<template>
<b-container>
    <b-row class="mb-3">
      <b-col>
        <b-form-group
          label="Per page"
          label-cols-sm="6"
          label-cols-md="4"
          label-cols-lg="3"
          label-align-sm="right"
          label-size="sm"
          label-for="perPageSelect"
          class="mb-0"
        >
          <b-form-select
            v-model="perPage"
            id="perPageSelect"
            size="sm"
            :options="pageOptions"
          ></b-form-select>
        </b-form-group>
      </b-col>

      <b-col>
        <b-pagination
          v-model="currentPage"
          :total-rows="totalRows"
          :per-page="perPage"
          size="sm"
          class="my-0"
        ></b-pagination>
      </b-col>

      <b-col>
        <b-form-spinbutton
          value=0.01
          min=0
          max=1
          step=0.01
          size="sm"
          placeholder=0
          v-model="threshold"
        />
      </b-col>
    </b-row>

    <!-- Main table element -->
    <b-table
      bordered
      show-empty
      small
      stacked="md"
      :items="results"
      :fields="fields"
      :current-page="currentPage"
      :per-page="perPage"
      :tbody-tr-class="delta_colour"
      :sort-compare="sortCompare"
      :filter="threshold_str"
      :filter-function="filter_results"
    >
    </b-table>
</b-container>
</template>

<script>
  export default {
    props: {
        results: null,
        pos: null,
        strand: null
    },
    methods: {
        sortCompare(aRow, bRow, key) {
          if (key === "dist_from_variant") return false
          const a = aRow[key] // or use Lodash `_.get()`
          const b = bRow[key]
          return Math.abs(a) > Math.abs(b) ? 1 : 0
        },
        round_score(value) {
            return value.toFixed(2)
        },
        delta_colour(item, type) {
            if (!item || type !== 'row') return null
            var max_delta = Math.max(Math.abs(item.donor), Math.abs(item.acceptor))
            if (max_delta > 0.001 & max_delta <= 0.1) return 'q1'
            if (max_delta > 0.1 & max_delta <= 0.2) return 'q2'
            if (max_delta > 0.2 & max_delta <= 0.3) return 'q3'
            if (max_delta > 0.3 & max_delta <= 0.4) return 'q4'
            if (max_delta > 0.4 & max_delta <= 0.5) return 'q5'
            if (max_delta > 0.5 & max_delta <= 0.6) return 'q6'
            if (max_delta > 0.6 & max_delta <= 0.7) return 'q7'
            if (max_delta > 0.7 & max_delta <= 0.8) return 'q8'
            if (max_delta > 0.8 & max_delta <= 0.9) return 'q9'
            if (max_delta > 0.9 & max_delta <= 1) return 'q10'
        },
        filter_results(row, filter) {
          if (Math.abs(row.donor) >= parseFloat(filter) | Math.abs(row.acceptor) >= parseFloat(filter)) {
            return true
          } else {
            return false
          }
        }
    },
    computed: {
      threshold_str() {
        return String(this.threshold)
      }
    },
    data() {
      return {
        threshold: 0.01,
        fields: [
          { key: 'dist_from_variant', 
            label: 'Position (relative to variant)', 
            sortable: true, 
            sortDirection: 'asc',
            sortByFormatted: true,
            formatter: (value) => {
              var position = parseInt(this.pos) + parseInt(value)
              return value + " (" + position + ")"
            }
          },
          { key: 'donor_ref', label: 'Donor REF', sortable: false, formatter: (value) => this.round_score(value) },
          { key: 'donor_alt', label: 'Donor VAR', sortable: false, formatter: (value) => this.round_score(value) },
          { key: 'donor', label: 'Donor Delta', sortable: true, formatter: (value) => this.round_score(value) },
          { key: 'acceptor_ref', label: 'Acceptor REF', sortable: false, formatter: (value) => this.round_score(value) },
          { key: 'acceptor_alt', label: 'Acceptor VAR', sortable: false, formatter: (value) => this.round_score(value) },
          { key: 'acceptor', label: 'Acceptor Delta', sortable: true, formatter: (value) => this.round_score(value) }
        ],
        totalRows: 1,
        currentPage: 1,
        perPage: 250,
        pageOptions: [50, 100, 250, 500, 1000]
      }
    },
    mounted() {
      // Set the initial number of items
      this.totalRows = this.results.length
    }
  }
</script>