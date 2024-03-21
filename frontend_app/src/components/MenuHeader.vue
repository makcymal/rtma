<template>
    <header class="head d-flex flex-wrap align-items-center justify-content-center justify-content-md-between py-3 mb-4 border-bottom">

      <ul class="nav col text-start">
        <li><button type="button" class="btn btn-primary ms-2" @click="homePush">Home</button></li>
        <li><button type="button" class="btn btn-primary me-2 ms-2" @click="monitoringPush">Monitoring</button></li>
        <li><button type="button" class="btn btn-primary me-2" @click="analiticsPush">Statistics</button></li>
      </ul>

      <div class="col text-center">
          <h3>Resources & Traffic Monitoring</h3>
      </div>

      <div class="col text-end">
        <button type="button" class="btn btn-primary me-2" @click="logoutPush" v-if="this.userAuthenticated">Logout</button>
        <button type="button" class="btn btn-primary me-2" @click="loginPush" v-if="!this.userAuthenticated">Login</button>
        <!-- <button type="button" class="btn btn-primary">Sign-up</button> -->
      </div>
    </header>
      
</template>
  
<script>
import {useUserDataStore} from "@/stores/UserDataStore"
import {mapStores, mapState, mapWritableState } from "pinia";
import axios from 'axios'

export default {
  
  name: 'MenuHeader',
  computed: {
    ...mapStores(useUserDataStore),
    ...mapState(useUserDataStore, ['userAuthenticated']),
    ...mapWritableState(useUserDataStore, ['userAuthenticated']),
  },
  mounted(){
    console.log(this.userAuthenticated)
  },
  methods: {
    logoutPush (){
      axios.post(axios.defaults.baseURL + "api/token/logout", {}, { withCredentials: true })
      .then((response) => {
            if(response.data.status === "OK"){
              this.userAuthenticated = false
              this.$router.push("/");
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
  background-color: #37c6e0
 }
  </style>
  