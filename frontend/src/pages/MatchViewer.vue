<template>
  <v-container class="fill-height" fluid style="background-color: var(--v-theme-surface);">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="pa-6" elevation="10" rounded="xl">
          <v-text-field
            v-model="inputId"
            @keyup.enter="handleSearch"
            placeholder="Enter Match ID or Account ID"
            hide-details
            variant="outlined"
            density="comfortable"
            class="mb-4"
          />

          <v-btn
            color="accent"
            block
            :loading="loading"
            :disabled="!/^\d+$/.test(inputId.trim())"
            @click="handleSearch"
          >
            Search
          </v-btn>

          <v-alert
            type="error"
            v-if="error"
            class="mt-4"
            dense
            text
          >
            {{ error }}
          </v-alert>

          <v-list two-line class="mt-4" v-if="messages.length">
            <v-list-item
              v-for="(msg, index) in messages"
              :key="index"
              class="mb-2"
            >
              <v-list-item-content>
                <v-list-item-title>{{ msg.author }}</v-list-item-title>
                <v-list-item-subtitle>{{ msg.text }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_BASE

const router = useRouter()
const inputId = ref('')
const messages = ref([])
const loading = ref(false)
const error = ref(null)

const handleSearch = async () => {
  const id = inputId.value.trim()
  if (!id) return

  loading.value = true
  error.value = null

  try {
    // First try to treat it as account ID
    await axios.get(`${API_BASE}/player-matches?account_id=${id}`)
    console.log("Account ID found:", id)
    router.push({ name: 'MyMatches', query: { account_id: id } })
  } catch (accountErr) {
    try {
      // Then try match ID fallback
      const { data } = await axios.get(`https://api.opendota.com/api/matches/${id}`)
      if (data.error != undefined) {
        throw new Error("Invalid match ID.")
      }
      console.log("data:", data)
      const hasParsed = data.od_data.has_parsed
      console.log("hasParsed:", hasParsed)
      if (!hasParsed) {
        console.log(await axios.get(`${API_BASE}/reparse-match?match_id=${data.match_id}`))
      }
      router.push({ name: 'MatchResults', params: { matchId: id } })
    } catch (matchErr) {
      error.value = matchErr.response?.data?.error || "Failed to fetch match data."
      if (error.value === "Not Found") {
        error.value = "Player or Match ID not valid"
      }
    }
  } finally {
    loading.value = false
  }
}
</script>
