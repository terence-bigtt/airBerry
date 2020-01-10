<template>
  <div id="app">
    <div>
      App Url: <b-form-input v-model="rootApi"/>
    </div>
    <highcharts :options="chartOptions"/>
    <br>
    <div>
      <button v-on:click="loadData">Refresh</button>
    </div>
    <br>
    <h1>Units</h1>
    <table>
      <tr>
        <th>Data</th>
        <th>Unit</th>
      </tr>
      <tr>
        <td>Temperature</td>
        <td>°C</td>
      </tr>
      <tr>
        <td>Humidity</td>
        <td>%</td>
      </tr>
      <tr>
        <td>NH3</td>
        <td>ppm</td>
      </tr>
      <tr>
        <td>PM10</td>
        <td>microgram / m<sup>3</sup></td>
      </tr>
      <tr>
        <td>PM2.5</td>
        <td>microgram / m<sup>3</sup></td>
      </tr>
    </table>
  </div>
</template>

<script>
    import {Chart} from 'highcharts-vue'
    import axios from "axios"
    import _ from "lodash"


    export default {
        components: {
            highcharts: Chart
        },
        data() {
            return {
                rootApi: "http://"+ window.location.hostname + ":5000",
                updateArgs: [true, true, {duration: 1000}],
                chartOptions: {
                    chart: {
                        zoomType: 'x'
                    },
                    title: {
                        text: 'Latest recorded values'
                    },
                    subtitle: {
                        text: document.ontouchstart === undefined ?
                            'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
                    },
                    xAxis: {
                        type: 'datetime'
                    },
                    series: [{
                        data: [] // sample data
                    }]
                }
            }
        },
        created() {
            this.loadData()
        },
        methods: {
            loadData() {
                let vm = this
                axios.get(this.rootApi + "/data").then(function (resp) {
                        let data = resp.data.data
                        let dataSeries = _.groupBy(data, d => d.name)
                        let series = _.map(dataSeries, function (values, key) {
                            console.log({values:values})
                            let series = _.map(values, v => [1000 * v.ts, v.value])
                            console.log(series)
                            return {name: key, data: series}
                        })
                        vm.$set(vm.chartOptions, "series", series)
                    }
                )
            }
        }
    }

</script>
