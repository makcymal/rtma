<template>
  <MenuHeader></MenuHeader>
  <img src="../assets/lit_logo.png" alt="" class="logo-image mx-auto d-block">
  <div class="d-flex justify-content-center">
      <div class="d-flex flex-column align-items-start">
        <div class="p-2">
          <h1 class="text-center">Система мониторинга трафика и загруженности системы</h1>
        </div>
        <div class="p-2">
          <h2 class="text-left">Страница мониторинга</h2>
          <p>Страница мониторинга имеет следующие 2 вида мониторинга: графики и таблица, 
            обновляющиеся в режиме реального времени</p>
        </div>
    </div>
  </div>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import {useMonitoringDataStore} from "@/stores/MonitoringDataStore"
import { mapActions, mapStores, mapState, mapWritableState } from "pinia";

export default {
    name: "MainPage",
    components: {
    MenuHeader
  },
  computed: {
    ...mapActions(useMonitoringDataStore, ['sendMessage']),
    ...mapStores(useMonitoringDataStore),
    ...mapState(useMonitoringDataStore, ['socket', 'serverMsgStd']),
    ...mapWritableState(useMonitoringDataStore, ['socket']),

  },
  mounted() {

  },
  methods: {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1 {
  font-family:'Calibri';
  font-weight: bold;
}

h2 {
  font-family:'Calibri';
  font-weight: bold;
}

.logo-image {
    width: 10%;
    height: auto;
   }
</style>