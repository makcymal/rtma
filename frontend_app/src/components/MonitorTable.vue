<template>
   <div class="container">
      <button class="btn btn-secondary" @click="showBatches">hlit</button>
   <template v-if="batchesVisible">
      <button v-for="(btnBatchName, btnIndex) in serverBatchesList" v-bind:key="btnIndex" @click="showTable(btnBatchName)"> {{ btnBatchName }}</button>
   </template>
   <template v-if="tableVisible">
   <div class="d-flex flex-column" style="margin: 0 !important; padding: 0 !important; align-items: center;">
      <div class="p-2" style="margin: 0 !important; padding: 0 !important;">
      <table class="table-bordered header-table">
         <thead>
            <tr class="header-cell">
               <th colspan="2" style="border-right-color: aliceblue;">INFO</th>
               <th v-for="(cField, cfindex) in serverTableHeaderStd.clustered_fields" v-bind:key="cfindex" :colspan=serverTableHeaderStd.clustered_fields_span[cfindex]>
                  {{  cField }}
               </th>
            </tr>
            <tr>
               <th> id </th>
               <th> name </th>
               <th v-for="(field, findex) in serverTableHeaderStd.fields" v-bind:key="findex">
                  {{ field }}</th>

            </tr>
         </thead>
      </table>
   </div>
   <div class="table-responsive hide-scroll p-2 custom-table" style="max-height: 500px; margin: 0 !important; padding: 0 !important;">
     <table class="table-bordered" style="margin: 0 !important; padding: 0 !important;">
       <tbody>
         <tr v-for="(compNode, nodeIndex) in serverMsgStd" v-bind:key="nodeIndex" :style="{backgroundColor: zebraTableColor(nodeIndex)}">
            <td>{{ nodeIndex + 1 }}</td>
            <td>{{ compNode.name }}</td>
            <td v-for="(fieldName, index) in serverTableHeaderStd.fields" v-bind:key="index"> {{ compNode[fieldName] }} {{ serverTableHeaderStd.fields_data_type[fieldName] }}</td>
         </tr>
       </tbody>
     </table>
   </div>
   <div class="p-2" style="margin: 0 !important; padding: 0 !important;">
   <table class="table-bordered footer-table">
         <tfoot>
            <tr class="footer-cell">
               <!-- заменить на td -->
               <th class="colspan-cell">AVERAGE</th> 
               <td v-for="(avgFieldName, avgIndex) in serverTableHeaderStd.fields" v-bind:key="avgIndex">{{ avgTotalData.avg[avgFieldName] }} {{ serverTableHeaderStd.fields_data_type[avgFieldName] }}</td>
            </tr>
            <tr class="footer-cell">
               <th class="colspan-cell"> TOTAL</th>
               <td v-for="(totalFieldName, totalIndex) in serverTableHeaderStd.fields" v-bind:key="totalIndex"> {{ avgTotalData.total[totalFieldName] }} {{ serverTableHeaderStd.fields_data_type[totalFieldName] }}</td>
            </tr>
         </tfoot>
      </table>
      </div>
   </div>
</template>
</div>
</template>
   
   
<script>
import {useMonitoringDataStore} from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState } from "pinia";

export default {
   name: "MonitorTable",
   data() {
      return {
      batchesVisible: false,
      tableVisible: false
      }
   },
   computed: {
      ...mapActions(useMonitoringDataStore, ['sendMessage']),
      ...mapStores(useMonitoringDataStore),
      ...mapState(useMonitoringDataStore, ['serverTableHeaderStd', 'serverMsgStd', 'avgTotalData', 'serverBatchesList']),
   },
   methods: {
      showBatches() {
         this.sendMessage('lsob');
         this.batchesVisible = true
      },
      showTable (batchName){
         this.sendMessage('head?' + batchName)
         this.sendMessage('mstd?' + batchName)
         this.tableVisible = true
      },
      zebraTableColor(index){
         if (index % 2){
            return '#ECECEC'
         } else {
            return '#FFFFFF'
         }
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
      background-color: rgb(241, 232, 232);
   }

   /* .footer-table {

   } */
   .colspan-cell {
      min-width: 22vh;
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
      min-width: 11vh;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
   }

   td {
      min-width: 11vh;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
   }

   .hide-scroll {
      scrollbar-width: none;
   }  
</style>