<template>
    <MenuHeader></MenuHeader>
    <div class="d-flex flex-column" style="align-items: center;">
      <div class="p-2">
         <button type="button" class="btn btn-light" @click="showBatches" id="hlit" :style="{backgroundColor: btnInactiveColor}">hlit</button>
      </div>
      <div class="p-2">
         <div class="btn-group btn-group-toggle">
         <template v-if="batchesVisible">
            <ul class="nav nav-pills mb-3" role="tablist">
            <li class="nav-item" role="presentation" v-for="(btnBatchName, btnIndex) in serverBatchesList" v-bind:key="btnIndex">
               <button class="btn btn-light" data-bs-toggle="pill" type="button" role="tab" aria-selected="false" @click="showTable(btnBatchName)">{{ btnBatchName }}</button>
            </li>
            </ul>
         </template>
         </div>
      </div>
      <div class="p2">
        <MonitorTable v-if="tableVisible" :server-msg="serverMsgStd" :server-table-header="serverTableHeaderStd" :avg-total-data="avgTotalData"></MonitorTable>
      </div>
    </div>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import MonitorTable from '@/components/MonitorTable.vue'
import {useMonitoringDataStore} from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState, mapWritableState } from "pinia";

export default {
    name: "MonitoringPage",
    components: {
    MenuHeader,
    MonitorTable
  },
  data() {
      return {
      batchesVisible: false,
      tableVisible: false,
      btnActiveColor: '#2F70AF',
      btnInactiveColor: '#e7d5f9',
      activeBatchTab: ""
      }
   },
   computed: {
      ...mapActions(useMonitoringDataStore, ['sendMessage']),
      ...mapStores(useMonitoringDataStore),
      ...mapWritableState(useMonitoringDataStore, ['currBatch', 'currLabel']),
      ...mapState(useMonitoringDataStore, ['serverTableHeaderStd', 'serverMsgStd', 'avgTotalData', 'serverBatchesList']),
   },
   methods: {
      showBatches() {
         if (!this.batchesVisible){
            this.sendMessage('lsob');
            this.batchesVisible = true
         }
      },
      showTable (batchName){
         this.sendMessage('head?' + batchName)
         this.sendMessage('mstd?' + batchName)
         this.tableVisible = true
         this.currBatch = batchName
      }
   }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>