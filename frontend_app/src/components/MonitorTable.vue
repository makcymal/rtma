<template>
   <div class="d-flex flex-column" style="margin: 0 !important; padding: 0 !important; align-items: center;">
      <div class="p-2" style="margin: 0 !important; padding: 0 !important;">
      <table class="table-bordered header-table">
         <thead>
            <tr class="header-cell">
               <th colspan="2" style="border-right-color: aliceblue;">INFO</th>
               <th v-for="(cField, cfindex) in serverTableHeader.clustered_fields" v-bind:key="cfindex" :colspan=serverTableHeader.clustered_fields_span[cfindex]>
                  {{ cField.toUpperCase() }}
               </th>
            </tr>
            <tr>
               <th> id </th>
               <th> name </th>
               <th v-for="(field, findex) in serverTableHeader.fields" v-bind:key="findex">
                  {{ field }}</th>
            </tr>
         </thead>
      </table>
   </div>
   <div class="table-responsive hide-scroll p-2 custom-table" style="max-height: 400px; margin: 0 !important; padding: 0 !important;">
     <table class="table-bordered" style="margin: 0 !important; padding: 0 !important;">
       <tbody>
         <tr v-for="(compNode, nodeIndex) in serverMsg" v-bind:key="nodeIndex" :style="{backgroundColor: zebraTableColor(nodeIndex)}">
            <td>{{ nodeIndex + 1 }}</td>
            <td v-if="!('name' in compNode)">thread{{ nodeIndex + 1 }}</td>
            <td v-else-if="!extDataOnName"> {{ compNode.name }}</td>
            <td v-else><button class="name-link btn btn-link" @click="showExtendedData(compNode.name)">{{ compNode.name }}</button></td>
            <td v-for="(fieldName, index) in serverTableHeader.fields" v-bind:key="index"> {{ compNode[fieldName] }} {{ serverTableHeader.fields_data_type[fieldName] }}</td>
         </tr>
       </tbody>
     </table>
   </div>
   <div class="p-2" style="margin: 0 !important; padding: 0 !important;">
   <table class="table-bordered footer-table">
         <tfoot>
            <tr class="footer-cell">

               <th class="colspan-cell">AVERAGE</th> 
               <template v-for="(avgFieldName, avgIndex) in serverTableHeader.fields" v-bind:key="avgIndex">
                  <td v-if="avgTotalData.avg[avgFieldName] !== '-'"> {{ avgTotalData.avg[avgFieldName] }} {{ serverTableHeader.fields_data_type[avgFieldName] }} </td>
                  <td v-else> {{ avgTotalData.avg[avgFieldName] }} </td>
               </template>
            
            </tr>
            <tr class="footer-cell">
               <th class="colspan-cell"> TOTAL</th>
               <template v-for="(totalFieldName, totalIndex) in serverTableHeader.fields" v-bind:key="totalIndex">
                  <td v-if="avgTotalData.total[totalFieldName] !== '-'"> {{ avgTotalData.total[totalFieldName] }} {{ serverTableHeader.fields_data_type[totalFieldName] }} </td>
                  <td v-else> {{ avgTotalData.total[totalFieldName] }} </td>
               </template>
            </tr>
         </tfoot>
      </table>
      </div>
   </div>
</template>
   
   
<script>
import { useMonitoringDataStore } from "@/stores/MonitoringDataStore"
import { mapStores, mapWritableState } from "pinia";
import { computeAvgTotalOutput } from '../utils/prettyMonTable'

export default {
   name: "MonitorTable",
   data() {
      return {
      }
   },
   computed: {
      avgTotalData (){
       return computeAvgTotalOutput(this.serverTableHeader['fields'], this.serverTableHeader['fields_data_type'], this.serverMsg)
      },
      ...mapStores(useMonitoringDataStore),
      ...mapWritableState(useMonitoringDataStore, ['currBatch', 'currLabel'])
   },
   props: ['serverTableHeader', 'serverMsg', 'extDataOnName'],
   methods: {
      zebraTableColor(index){
         if (index % 2){
            return '#ECECEC'
         } else {
            return '#FFFFFF'
         }
      },
      showExtendedData(nodeLabel){
         this.currLabel = nodeLabel
         this.$router.push('/monitoring/node')
      }
   }
}
</script>
   
   
<style>

   .header-cell {
      background-color: rgb(160, 105, 209);
      color: white;
      border: 1px solid black;
      min-height: 20vh;
   }

   .footer-cell {
      background-color: rgb(234, 201, 201);
   }

   /* .footer-table {

   } */
   .colspan-cell {
      min-width: 12vw;
   }

   .header-table {
      border: 1x solid black;
      border-radius: 1px;
   }

   .custom-table {
      -webkit-box-shadow: inset 0px 0px 3px 1px rgba(41,49,51,1);
      -moz-box-shadow: inset 0px 0px 3px 1px rgba(41,49,51,1);
      box-shadow: inset 0px 0px 3px 1px rgba(41,49,51,1);
   }

   tr {
      margin: 5px;
      padding: 5px;
   }

   th {
      min-width: 6vw;
      max-width: 6vw;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
      word-break: break-all;
   }

   td {
      min-width: 6vw;
      max-width: 6vw;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
      word-break: break-all;
   }
   .name-link {
      margin: 0px;
      padding: 0px;
      min-width: 5vw;
      max-width: 5vw;
      word-break: break-all;
   }

   .hide-scroll {
      scrollbar-width: none;
   }  
</style>