<template>
    <header class="head d-flex flex-wrap align-items-center justify-content-center justify-content-md-between py-3 mb-4 border-bottom">

      <ul class="nav col text-start">
        <li><a href="/" type="button" class="btn btn-primary ms-2">Home</a></li>
        <li><button type="button" class="btn btn-primary me-2 ms-2">Monitoring</button></li>
        <li><button type="button" class="btn btn-primary me-2">Statistics</button></li>
      </ul>

      <div class="col text-center">
          <h1>Traffic Monitoring</h1>
      </div>

      <div class="col text-end">
        <a href="login" type="button" class="btn btn-primary me-2">Login</a>
        <!-- <button type="button" class="btn btn-primary">Sign-up</button> -->
      </div>
    </header>
      
</template>
  
  <script>
  export default {
    name: 'MenuHeader',
    props: {
      msg: String
    }
  }
  </script>
  
  <!-- Add "scoped" attribute to limit CSS to this component only -->
  <style scoped>
 .head {
  background-color: #37c6e0
 }
  </style>
  