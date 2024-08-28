<template>
    <header class="shadow-sm head d-flex flex-wrap align-items-center justify-content-center justify-content-md-between py-3 mb-4 border-bottom">

      <ul class="nav col text-start">
        <li><button type="button" class="btn btn-primary ms-2 nav-button" @click="homePush">Home</button></li>
        <li><button type="button" class="btn btn-primary ms-2 nav-button" @click="monitoringPush">Monitoring</button></li>
        <li><button type="button" class="btn btn-primary me-2 ms-2 nav-button" @click="analiticsPush">Statistics</button></li>
      </ul>

      <div class="col text-center">
          <h2 style="color: #000046;">Resources & Traffic Monitoring</h2>
      </div>

      <div class="col text-end">
        <button type="button" class="btn btn-primary me-2 nav-button" @click="profilePush" v-if="this.userAuthenticated">Profile</button>
        <button type="button" class="btn btn-primary me-2 nav-button" @click="logoutPush" v-if="this.userAuthenticated">Logout</button>
        <button type="button" class="btn btn-primary me-2 nav-button" @click="loginPush" v-if="!this.userAuthenticated">Login</button>
        <!-- <button type="button" class="btn btn-primary">Sign-up</button> -->
      </div>
    </header>
      
</template>
  
<script>
import {useUserDataStore} from "@/stores/UserDataStore"
import {useMonitoringDataStore} from '@/stores/MonitoringDataStore'
import {mapStores, mapState, mapWritableState, mapActions } from "pinia";
import axios from 'axios'

export default {
  
  name: 'MenuHeader',
  computed: {
    ...mapStores(useUserDataStore),
    ...mapStores(useMonitoringDataStore),
    ...mapState(useUserDataStore, ['userAuthenticated']),
    ...mapWritableState(useUserDataStore, ['userAuthenticated']),
    ...mapActions(useMonitoringDataStore, ['sendMessage']),
  },
  mounted(){
    
  },
  methods: {
    logoutPush (){
      axios.post(axios.defaults.baseURL + "api/token/logout", {}, { withCredentials: true })
      .then((response) => {
            if(response.data.status === "OK"){
              this.userAuthenticated = false
              this.$router.push("/").then(() => {
                window.location.reload()
              });
            }
          })
    },
    loginPush(){
      this.$router.push("/login");
    },
    homePush(){
      this.$router.push("/");
    },
    monitoringPush(){
      this.$router.push("/monitoring");
      // // this.sendMessage('lsob')
      // // TODO: оставить только lsob
      // this.sendMessage('head')
      // this.sendMessage('mstd')
    },
    analiticsPush(){
      this.$router.push("/analitics");
    },
    profilePush(){
      this.$router.push("/profile");
    },
  }
  // props: {
  //   userAuthorized: Boolean
  // }
}
</script>
  
  <!-- Add "scoped" attribute to limit CSS to this component only -->
  <style scoped>
 .head {
  background-color: #01B0F1
 }

 .nav-button {
  background-color: #000046;
 }
  </style>
  