<template>
  <v-container fluid class="pa-8 fill-height" style="background-color: var(--v-theme-surface);">
    <v-row v-if="loading" align="center" justify="center" class="fill-height">
      <v-col cols="auto">
        <v-progress-circular indeterminate size="50" color="accent" />
      </v-col>
    </v-row>

    <v-row v-else justify="center">
      <v-col cols="12">
        <h2 class="text-white mb-1">🎮 Recent Matches for <strong>{{ playerName }}</strong></h2>

        <v-table class="transparent-list text-white" dense>
          <thead>
            <tr>
              <th>Hero</th>
              <th>Date</th>
              <th>Result</th>
              <th>Team</th>
              <th>Duration</th>
              <th>Kills</th>
              <th>Deaths</th>
              <th>Assists</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="match in matches"
              :key="match.match_id"
              class="hoverable"
              @click="goToMatch(match.match_id)"
            >
              <td class="d-flex align-center">
                <v-avatar size="40">
                  <v-img :src="getHeroImage(match.hero_id)" :alt="match.hero_name" />
                </v-avatar>
                <span class="ml-3 font-weight-medium">{{ getHeroName(match.hero_id) }}</span>
              </td>
              <td>{{ formatDate(match.start_time) }}</td>
              <td>
                <span class="match-result" :class="getMatchResultClass(match)">
                  {{ getMatchResultText(match) }}
                </span>
              </td>
              <td>{{ getTeam(match) }}</td>
              <td>{{ formatDuration(match.duration) }}</td>
              <td>{{ match.kills }}</td>
              <td>{{ match.deaths }}</td>
              <td>{{ match.assists }}</td>
            </tr>
          </tbody>
        </v-table>

        <div class="d-flex justify-center align-center mt-4 gap-4">
          <v-pagination
            v-model="currentPage"
            :length="totalPages"
            color="accent"
            @update:modelValue="loadMatches"
            :total-visible="7"
          />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_BASE

const router = useRouter()
const route = useRoute()
const matches = ref([])
const loading = ref(true)
const heroImageMap = ref({})
const heroNameMap = ref({})
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 20
const accountId = ref(route.query.account_id || null)
const playerName = ref('You')

const goToMatch = (matchId) => {
  router.push({ name: 'MatchResults', params: { matchId } })
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (unix) => {
  const date = new Date(unix * 1000)
  return date.toLocaleDateString()
}

const getHeroImage = (heroId) => {
  return heroImageMap.value[heroId] || ''
}

const getHeroName = (heroId) => {
  return heroNameMap.value[heroId] || 'Unknown Hero'
}

const getTeam = (match) => {
  return match.player_slot < 128 ? 'Radiant' : 'Dire'
}

const getMatchResultText = (match) => {
  const isRadiant = match.player_slot < 128
  const didWin = (isRadiant && match.radiant_win) || (!isRadiant && !match.radiant_win)
  return didWin ? 'Victory' : 'Defeat'
}

const getMatchResultClass = (match) => {
  const isRadiant = match.player_slot < 128
  const didWin = (isRadiant && match.radiant_win) || (!isRadiant && !match.radiant_win)
  return didWin ? 'win' : 'loss'
}

const loadMatches = async () => {
  try {
    loading.value = true
    const offset = (currentPage.value - 1) * pageSize
    const url = accountId.value
      ? `${API_BASE}/player-matches?account_id=${accountId.value}&offset=${offset}`
      : `${API_BASE}/player-matches?offset=${offset}`

    const playerRes = await axios.get(url, { withCredentials: true })
    matches.value = playerRes.data.matches
    playerName.value = playerRes.data.player?.profile?.personaname || 'You'
  } catch (err) {
    console.error("Failed to load matches", err)
  } finally {
    loading.value = false
  }
}

const loadTotalPages = async () => {
  try {
    const url = accountId.value
      ? `${API_BASE}/win-lose-amount?account_id=${accountId.value}`
      : `${API_BASE}/win-lose-amount`

    const res = await axios.get(url, { withCredentials: true })
    const totalMatches = res.data.win + res.data.lose
    totalPages.value = Math.ceil(totalMatches / pageSize)
    console.log("res:", res)
    console.log("Total matches:", totalMatches)
  } catch (err) {
    console.error("Failed to load match count", err)
  }
}

watch(currentPage, loadMatches)

onMounted(async () => {
  await loadTotalPages()
  await loadMatches()

  const heroRes = await fetch('/heroes.json')
  const heroData = await heroRes.json()
  for (const hero of Object.values(heroData)) {
    heroImageMap.value[hero.id] = `https://cdn.cloudflare.steamstatic.com${hero.img}`
    heroNameMap.value[hero.id] = hero.localized_name
  }
})
</script>

<style scoped>
.text-white {
  color: white;
}
.transparent-list {
  background-color: transparent !important;
}
.hoverable {
  cursor: pointer;
  transition: background-color 0.2s;
}
.hoverable:hover {
  background-color: rgba(255, 255, 255, 0.05);
}
.match-result {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  color: white;
  background-color: gray;
}
.match-result.win {
  background-color: #4caf50;
}
.match-result.loss {
  background-color: #f44336;
}
</style>