<template>
   <div class="card shadow text-center chart-card align-items-center">
      <h3>{{ this.clusterLabel }}, {{ this.getChartDataType() }}</h3>
      <Bar
      id="my--bar-chart-id"
      :options="chartOptions"
      :data="chartData"
      :key="inverted"
   />
   <div class="d-flex align-items-center form-check form-switch justify-content-center">
      <input class="form-check-input mx-1" type="checkbox" role="switch" id="flexSwitchCheckbox" v-on:input="invertChart">
      <label class="form-check-label mx-1" for="flexSwitchCheckbox">Inverted</label>
   </div>
   </div>
</template>
   

<script>
import { Chart as ChartJS, Tooltip, Legend, CategoryScale, LinearScale,  BarElement } from 'chart.js'
import { Bar } from 'vue-chartjs'
import { computeAvgTotalOutput } from '../utils/prettyMonTable'

ChartJS.register(Tooltip, Legend, CategoryScale, LinearScale, BarElement)

export default {
  name: 'MonitorBarChart',
  components: { Bar },
  props: ['clusterLabel', 'serverData', 'serverFields', 'serverFieldsDataType'],
  data() {
    return {
      inverted: false,
      chartOptions: {
         indexAxis: 'x',
         responsive: true,
         plugins: {
            legend: {
            display: false
            }
            }
         }
      }
   },
  computed: {
   chartData () {
        return {datasets: [ { data: Object.values(this.transformData(computeAvgTotalOutput(this.serverFields, this.serverFieldsDataType, this.serverData).avg)),

         backgroundColor: ['#669900', '#ccee66', '#006699', '#3399cc', '#990066', '#cc3399',
         '#ff6600', '#ffcc00', '#bce3fa', '#cb0b0a'] } ],

         labels: Object.keys(this.transformData(computeAvgTotalOutput(this.serverFields, this.serverFieldsDataType, this.serverData).avg)) }
      }
   },
  methods: {
   transformData (inputData) {
      let keys = this.filterKeys(this.serverFields, inputData)
      let data = {}
      for (let key of keys){
         data[key] = inputData[key]
      }
      return this.sortData(data)
   },
   filterKeys (keys, data) {
      let newKeys = []
      for (let key of keys){
         if (this.serverFieldsDataType[key] != 'hz' && (typeof data[key] === "number" || typeof data[key] === "bigint")){
            newKeys.push(key)
         }
      }
      return newKeys
   },
   getChartDataType () {
      return this.serverFieldsDataType[this.serverFields[0]]
   },
   sortData (data){
      let newData = {}

      // Create items array
      let items = Object.keys(data).map(function(key) {
      return [key, data[key]];
      });

      // Sort the array based on the second element
      items.sort(function(first, second) {
      return second[1] - first[1];
      });

      for (let i = 0; i < items.length; i++){
         newData[items[i][0]] = items[i][1]
      }
         return newData
   },
   invertChart (){
      this.inverted = !this.inverted
      if (this.inverted){
         this.chartOptions.indexAxis = 'y'
      } else{
         this.chartOptions.indexAxis = 'x'
      }
   }
  }
}
</script>
   
   
<style scoped> 
 .chart-card {
   width: 23vw; 
   padding-bottom: 2vh; 
   padding-top: 2vh;
 }

 input[type=checkbox]
{
  /* Double-sized Checkboxes */
  -ms-transform: scale(1.7); /* IE */
  -moz-transform: scale(1.7); /* FF */
  -webkit-transform: scale(1.7); /* Safari and Chrome */
  -o-transform: scale(1.7); /* Opera */
  transform: scale(1.7);
  padding: 5px;
}

label[for=flexSwitchCheckbox]
{
   padding-left: 20%;
   font-size: 115%;
}

</style>