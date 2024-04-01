<template>
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
                  {{ field }} </th>

            </tr>
         </thead>
      </table>
   </div>
   <div class="table-responsive hide-scroll p-2 custom-table" style="max-height: 500px; margin: 0 !important; padding: 0 !important;">
     <table class="table-bordered" style="margin: 0 !important; padding: 0 !important;">
       <tbody>
         <tr v-for="(compNode, nodeIndex) in serverMsgStd" v-bind:key="nodeIndex">
            <td>{{ nodeIndex }}</td>
            <td>{{ compNode.name }}</td>
            <td v-for="(fieldName, index) in serverTableHeaderStd.fields" v-bind:key="index"> {{ compNode[fieldName] }}</td>
         </tr>
       </tbody>
     </table>
   </div>
   <div class="p-2" style="margin: 0 !important; padding: 0 !important;">
   <table class="table-bordered footer-table">
         <tfoot>
            <tr class="footer-cell">
               <!-- заменить на td -->
               <th class="colspan-cell">TOTAL</th> 
               <th>sys</th>
               <th>user</th>
               <th>nice</th>
               <th>iowait</th>
               <th>idle</th>
               <th>idle</th>
               <th>idle</th>
            </tr>
            <tr class="footer-cell">
               <th class="colspan-cell"> AVERAGE</th>
               <th>sys</th>
               <th>user</th>
               <th>nice</th>
               <th>iowait</th>
               <th>idle</th>
               <th>idle</th>
               <th>idle</th>
            </tr>
         </tfoot>
      </table>
      </div>
   </div>
</template>
   
   
<script>
import {useMonitoringDataStore} from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState } from "pinia";

export default {
   name: "MonitorTable", 
   computed: {
      ...mapActions(useMonitoringDataStore, ['sendMessage']),
      ...mapStores(useMonitoringDataStore),
      ...mapState(useMonitoringDataStore, ['serverTableHeaderStd', 'serverMsgStd']),
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
      min-width: 20vh;
      min-height: 20vh;
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
      min-width: 15vh;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
   }

   td {
      min-width: 15vh;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
   }

   .hide-scroll {
      scrollbar-width: none;
   }  
</style>