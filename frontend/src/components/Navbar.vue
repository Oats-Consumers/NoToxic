<template>
  <v-app-bar app dark color="#0E3A4F" elevation="6">
    <!-- Left: App title -->
    <v-btn text to="/" class="pl-2">
      <span class="text-h6 font-weight-bold white--text">Toxicity Ward ☣️</span>
    </v-btn>

    <v-spacer />
  </v-app-bar>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_BASE
</script>
