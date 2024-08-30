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
            <p>Страница Monitoring имеет следующие 2 вида мониторинга: графики и таблица, 
              обновляющиеся в режиме реального времени. <br>
              На странице есть следующий выбор элементов: Кластер, группы серверов, выбор режима отображения (таблица или график) <br> и выбор типа графика.
            </p>

            <p class="text-center">
              <img src="../assets/mon_menu.jpg" alt="" style="border: 1px solid gray; width: 200px; height: 'auto'">
            </p>

            <p>
              Графики имеют 2 типа: Pie (круговая диаграмма) и Bar (Гистограмма). У круговой диаграммы имеется функционал отключения 
              <br> определенных данных и разделения на части (sliced). Гистограмма имеет функционал поворота на 90 градусов (Inverted).
            </p>
            
            <p class="text-center">
              <img src="../assets/pie_chart_example.jpg" alt="" style="border: 1px solid gray; width: 900px; height: 'auto'">
            </p>

            <p class="text-center">
              <img src="../assets/bar_chart_example.jpg" alt="" style="border: 1px solid gray; width: 900px; height: 'auto'">
            </p>

            <p>
              Таблица отображает загрузку всех компьютеров внутри выбранной группы. Таблица поддерживает скролл <br> внутренней ее части. 
              Высокая загрузка компонента компьютера помечается оттенками желтого цвета.
            </p>

            <p class="text-center">
              <img src="../assets/table_example.jpg" alt="" style="border: 1px solid gray; width: 900px; height: 'auto'">
            </p>

        </div>
        <div class="p-2">
          <h2 class="text-left">Страница расширенного мониторинга</h2>

            <p>
              Для перехода в просмотр расширенного мониторинга требуется нажать на название нужного компьютера 
              <br> в таблице мониторинга. Расширенный мониторинг отображает характеристики компьютера  <br> 
              и таблицу мониторинга отдельных компонентов компьютера.
            </p>

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
    width: 9%;
    height: auto;
   }

.text-image {
width: 990px;
height: auto;
border: 1px solid gray;
}
</style>