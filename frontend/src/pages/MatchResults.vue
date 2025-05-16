<template>
  <v-container fluid class="pa-8 fill-height" style="background-color: var(--v-theme-surface);">
    <!-- Loading view -->
    <v-row v-if="loading" align="center" justify="center" class="fill-height">
      <v-col cols="auto">
        <v-progress-circular indeterminate size="50" color="accent" />
      </v-col>
    </v-row>

    <!-- Loaded chat content -->
    <v-row v-else justify="center">
      <v-col cols="10">
        <h2 class="text-white mb-2">
          🧾 Chat Summary for Match {{ matchId }}
        </h2>

        <v-list dense class="transparent-list">
          <v-list-item
            v-for="(msg, index) in messages"
            :key="index"
            class="chat-row hoverable"
            @click="selectedMessage = msg"
          >
            <div class="chat-line">
              <!-- Time -->
              <div class="chat-time">{{ msg.time_str }}</div>

              <!-- Avatar -->
              <v-avatar size="32">
                <v-img :src="getHeroImage(msg.hero_id)" />
              </v-avatar>

              <!-- Player info -->
              <div class="chat-player">
                <div class="player-name"><strong>{{ msg.player_name }}</strong></div>
                <div class="hero-name text-muted">({{ msg.hero_name }})</div>
              </div>

              <!-- Message -->
              <div
                class="chat-message"
                :style="{ color: msg.label.trim() === 'toxic' ? '#ff5e5e' : '#91f291' }"
              >
                {{ msg.msg }}
              </div>
            </div>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>

    <!-- Dialog -->
    <v-dialog v-model="selectedMessage" max-width="600">
      <v-card :color="selectedMessage?.label.trim() === 'toxic' ? 'red darken-3' : 'green darken-3'" dark>
        <v-card-title class="text-h6">
          🧝 {{ selectedMessage?.hero_name }} ({{ selectedMessage?.hero_name }})
        </v-card-title>
        <v-card-text>
          <v-img :src="getHeroImage(selectedMessage?.hero_id)" height="150" contain class="mb-3" />
          <p><strong>🕐 Time:</strong> {{ selectedMessage?.time_str }}</p>
          <p><strong>💬 Message:</strong> {{ selectedMessage?.msg }}</p>
          <p><strong>🚩 Toxic:</strong> {{ selectedMessage?.label.trim() === 'toxic' ? 'Yes' : 'No' }}</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="selectedMessage = null">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
const API_BASE = import.meta.env.VITE_API_BASE

const route = useRoute()
const matchId = route.params.matchId
const messages = ref([])
const loading = ref(true)
const selectedMessage = ref(null)
const heroImageMap = ref({})

onMounted(async () => {
  try {
    loading.value = true

    const res = await fetch(`${API_BASE}/label-chat?match_id=${matchId}`)
    messages.value = await res.json()

    const heroRes = await fetch('/heroes.json')
    const heroData = await heroRes.json()
    for (const hero of Object.values(heroData)) {
      heroImageMap.value[hero.id] = `https://cdn.cloudflare.steamstatic.com${hero.img}`
    }
  } catch (err) {
    console.error("Failed to fetch messages or hero data", err)
  } finally {
    loading.value = false
  }
})

const getHeroImage = (heroId) => {
  return heroImageMap.value[heroId] || ''
}
</script>

<style scoped>
.text-white {
  color: white;
}
.transparent-list {
  background-color: transparent !important;
}

/* Overwrite Vuetify padding (16px) and apply 10px all sides */
.chat-row {
  display: flex;
  align-items: center;
  padding: 10px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.hoverable {
  cursor: pointer;
  transition: background-color 0.15s;
}
.hoverable:hover {
  background-color: rgba(255, 255, 255, 0.05);
}
.chat-line {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.chat-time {
  min-width: 50px;
  text-align: center;
  color: #ccc;
  font-size: 0.95rem;
}
.chat-player {
  display: flex;
  align-items: center;
  gap: 12px; /* 👈 Same spacing as outer .chat-line */
  color: #fff;
  font-weight: 500;
  font-size: 1rem;
  flex-shrink: 0; /* Prevent shrinking */
  flex-grow: 0;   /* Don't allow expansion to take extra space */
}

.player-name,
.hero-name {
  white-space: nowrap;
}

.chat-message {
  font-size: 1.1rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-grow: 1;
}
.text-muted {
  color: #aaa;
  font-weight: 400;
}
</style>
