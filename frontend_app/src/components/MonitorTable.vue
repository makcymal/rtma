<template>
   <div class="d-flex flex-column" style="margin: 0 !important; padding: 0 !important; align-items: center;">
      <div class="p-2" style="margin: 0 !important; padding: 0 !important;">
      <table class="table-bordered header-table">
         <thead>
            <tr class="header-cell">
               <th colspan="4" style="border-right-color: aliceblue;">INFO</th>
               <th colspan="5" >CPU</th>
            </tr>
            <tr>
               <!-- info -->
               <th>id</th>
               <th>name</th>
               <th>cores</th>
               <th>load</th>

               <!-- cpu -->
               <th>sys</th>
               <th>user</th>
               <th>nice</th>
               <th>iowait</th>
               <th>idle</th>

            </tr>
         </thead>
      </table>
   </div>
   <div class="table-responsive hide-scroll p-2 custom-table" style="max-height: 500px; margin: 0 !important; padding: 0 !important;">
     <table class="table-bordered" style="margin: 0 !important; padding: 0 !important;">
       <tbody>
         <tr v-for="(info, index) in tableInfo" v-bind:key="index">
            <td>{{index}}</td>
            <td>{{info.name}}</td>
            <td>{{info.cores}}</td>
            <td>{{ info.load }}</td>
            <td>{{ info.sys }}</td>
            <td>{{ info.user }}</td>
            <td>{{ info.nice }}</td>
            <td>{{ info.iowait }}</td>
            <td>{{ info.idle }}</td>
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
   export default {
       name: "MonitorTable",
       data() {
         return {
            tableInfo: [{"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            {"id": 1, "name": "dgx01", "cores": 80, "load": 4, "sys": "0 %", "user": "5 %", "nice": "0 %", "iowait": "0 %", "idle": "95 %"},
            ]
         }
       }
   }
   </script>
   
   
<style>

   .header-cell {
      background-color: rgb(160, 105, 209);
      color: white;
      border: 1px solid black;
   }

   .footer-cell {
      background-color: rgb(241, 232, 232);
   }

   /* .footer-table {

   } */
   .colspan-cell {
      width: 20vh;
      height: 5vh;
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
      padding: 5px;
      margin: 5px;
   }

   th {
      width: 10vh;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
   }

   td {
      width: 10vh;
      height: 5vh;
      text-align: center; 
      vertical-align: middle;
   }

   .hide-scroll {
      scrollbar-width: none;
   }  
</style>