<template>
    <MenuHeader></MenuHeader>
    <MonitorTable></MonitorTable>
</template>

<script>
import MenuHeader from '@/components/MenuHeader.vue'
import MonitorTable from '@/components/MonitorTable.vue'

export default {
    name: "MonitoringPage",
    components: {
    MenuHeader,
    MonitorTable
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>