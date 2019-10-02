<template>
  <div id="app">
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
                rootApi: process.env.VUE_APP_ROOT_API,
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
                axios.get(this.rootApi+"/data").then(function (resp) {
                        let data = resp.data
                        let keys = []
                        data.data.forEach(function (datum) {
                            let newKeys = _.filter(_.keys(datum), function (key) {
                                return key !== "ts" && key !== "time"
                            })
                            newKeys.forEach(function (newKey) {
                                if (!_.includes(keys, newKey)) {
                                    keys.push(newKey)
                                }
                            })
                        })
                        let series = _.map(keys, function (key) {
                            let seriesData = []
                            data.data.forEach(function (datum) {
                                if (datum[key]) {
                                    seriesData.push([1000 * datum["ts"], datum[key]])
                                }
                            })
                            seriesData = _.sortBy(seriesData, datum => datum[0])
                            return {
                                data: seriesData,
                                name: key
                            }
                        })
                        vm.$set(vm.chartOptions, "series", series)
                    }
                )
            }
        }
    }

</script>
