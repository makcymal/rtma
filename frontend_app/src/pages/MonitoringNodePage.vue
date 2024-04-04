<template>
    <MenuHeader></MenuHeader>
    <div class="d-flex flex-column" style="align-items: center;">
      <div class="p2" v-for="(key, index) in Object.keys(serverTableHeaderExt)" v-bind:key="index" style="margin: 10px;">
        <MonitorTable :server-msg="serverMsgExt[key]" :server-table-header="formatHeader(serverTableHeaderExt[key], key)" :avg-total-data="formatAvgTotal(serverMsgExt)"></MonitorTable>
      </div>
    </div>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import MonitorTable from '@/components/MonitorTable.vue'
import { useMonitoringDataStore } from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState } from "pinia";

export default {
    name: "MonitoringNodePage",
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
      ...mapState(useMonitoringDataStore, ['serverTableHeaderExt', 'serverMsgExt', 'avgTotalData', 'serverBatchesList', 'currBatch', 'currLabel']),
   },
   mounted() {
    console.log('sended 2')
    this.sendMessage('spec?' + this.currBatch + '?' + this.currLabel)
    this.sendMessage('desc?' + this.currBatch + '?' + this.currLabel)
    this.sendMessage('mext?' + this.currBatch + '?' + this.currLabel)
  },
   methods: {
      formatHeader (headerData, key){
        let formattedData = {} // new header data formatted to fill the table

        formattedData['clustered_fields'] = [key]
        formattedData['clustered_fields_span'] = [Object.keys(headerData).length]
        formattedData['fields'] = Object.keys(headerData);
        formattedData['fields_data_type'] = Object.values(headerData);
        return formattedData
      },
      formatTableData (tableData){
        return tableData
      },
      formatAvgTotal (tableData){
        console.log('111', tableData, this.serverMsgExt)
        return {avg: {}, total: {}}
      }
   }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>