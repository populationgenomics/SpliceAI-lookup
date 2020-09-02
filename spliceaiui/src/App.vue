<template>
  <div id="app">
    <SpliceAI msg="SpliceAI Tools"/>
  </div>
</template>

<script>
import SpliceAI from './components/SpliceAI.vue'

export default {
  name: 'App',
  components: {
    SpliceAI
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
