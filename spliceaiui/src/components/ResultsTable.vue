<template>
<b-container>
    <b-row>
      <b-col sm="5" md="6" class="my-1">
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

      <b-col sm="7" md="6" class="my-1">
        <b-pagination
          v-model="currentPage"
          :total-rows="totalRows"
          :per-page="perPage"
          size="sm"
          class="my-0"
        ></b-pagination>
      </b-col>
    </b-row>

    <!-- Main table element -->
    <b-table
      bordered
      show-empty
      small
      striped
      stacked="md"
      :items="results"
      :fields="fields"
      :current-page="currentPage"
      :per-page="perPage"
      :tbody-tr-class="delta_colour"
      :sort-compare="sortCompare"
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
            if (!item || type !== 'row') return
            if (item.donor <= -0.2 | item.acceptor <= -0.2) return 'table-danger'
            if (item.donor >= 0.2 | item.acceptor >= 0.2) return 'table-warning'
        }
    },
    data() {
      return {
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