<template>
  <div class="q-pa-md">
    <q-table
      :class="$q.dark.isActive?'my-sticky-header-last-column-table-dark' : 'my-sticky-header-last-column-table'"
      flat
      bordered
      :rows="rows"
      :columns="columns"
      row-key="name"
      :pagination="pagination"
      separator="cell"
      :no-data-label="t('nodata')"
      :rows-per-page-label="t('per_page')"
      :rows-per-page-options="[1,10,30,50,200,0]"
      :table-style="{ height: ScreenHeight, width: ScreenWidth }"
      :card-style="{ backgroundColor: CardBackground }"
      @request="onRequest"

    >
      <template v-slot:top="props">
        <q-btn-group flat>
          <q-btn :label="t('refresh')" icon="refresh" @click="onRequest()" v-show="tokenStore.userPermissionGet('Get User List')">
            <q-tooltip class="bg-indigo" :offset="[10, 10]" content-style="font-size: 12px">{{ t('refreshdata') }}</q-tooltip>
          </q-btn>
          <q-btn :label="t('new')" icon="add" v-show="tokenStore.userPermissionGet('Create One User')">
            <q-tooltip class="bg-indigo" :offset="[10, 10]" content-style="font-size: 12px">{{ t('newUser') }}</q-tooltip>
          </q-btn>
        </q-btn-group>
        <q-space />
        <q-input dense debounce="300" color="primary" v-model="search" @input="onRequest()" @keyup.enter="onRequest()">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
        <q-btn
          flat round dense
          :icon="props.inFullscreen ? 'fullscreen_exit' : 'fullscreen'"
          @click="props.toggleFullscreen"
        />
      </template>

      <template v-slot:body-cell="props">
        <q-td :props="props">
          <div v-if="props.col.name === 'action'">
            <q-btn round flat icon="published_with_changes">
              <q-tooltip class="bg-indigo" :offset="[10, 10]" content-style="font-size: 12px">{{ t('changepassword') }}</q-tooltip>
            </q-btn>
            <q-btn round flat icon="admin_panel_settings">
              <q-tooltip class="bg-indigo" :offset="[10, 10]" content-style="font-size: 12px">{{ t('permission') }}</q-tooltip>
            </q-btn>
            <q-btn round flat icon="lock_person" v-show="!props.row.is_active">
              <q-tooltip class="bg-indigo" :offset="[10, 10]" content-style="font-size: 12px">{{ t('isnotactive') }}</q-tooltip>
            </q-btn>
            <q-btn round flat icon="lock_open" v-show="props.row.is_active">
              <q-tooltip class="bg-indigo" :offset="[10, 10]" content-style="font-size: 12px">{{ t('isactive') }}</q-tooltip>
            </q-btn>
            <q-btn round flat icon="delete_sweep">
              <q-tooltip class="bg-indigo" :offset="[10, 10]" content-style="font-size: 12px">{{ t('deleteuser') }}</q-tooltip>
            </q-btn>
          </div>
          <div v-else>
            {{ props.value }}
          </div>
        </q-td>
      </template>

      <template v-slot:pagination="scope">
        {{ t('total') }}{{ pagesNumber }} {{ t('page') }}
        <q-pagination
          v-model="scope.pagination.page"
          :max="scope.pagesNumber"
          input
          input-class="text-orange-10"
          @update:model-value="PageChanged(scope)"
        />
      </template>

    </q-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from "vue-i18n"
import { get } from 'boot/axios'
import { useTokenStore } from 'stores/token'

const { t } = useI18n()
const $q = useQuasar()
const tokenStore = useTokenStore()

const columns = computed( () => [
  {
    name: 'username', required: true, label: t('username'), align: 'left', field: 'username' },
  { name: 'email', align: 'center', label: t('email'), field: 'email' },
  { name: 'date_joined', label: t('date_joined'), field: 'date_joined' },
  { name: 'last_login', label: t('last_login'), field: 'last_login' },
  { name: 'updated_time', label: t('updated_time'), field: 'updated_time' },
  { name: 'action', label: t('action'), align: 'right' }
])

const rows = ref( [])

const search = ref( '')

const rowsCount = ref(0)

const pagination  = ref({
    page: 1,
    rowsPerPage: 1,
    rowsNumber: 1
  })

const pagesNumber = computed( () => {
  if (token.value !== '') {
    return Math.ceil(rowsCount.value / pagination.value.rowsPerPage)
  } else {
    return 0
  }
})

const ScreenHeight = ref($q.screen.height * 0.73 + '' + 'px')
const ScreenWidth = ref($q.screen.width * 0.825 + '' + 'px')
const CardBackground = ref($q.dark.isActive? '#121212' : '#ffffff')

const token = computed(() => tokenStore.token)

function onRequest (props) {
  let requestData = {}
  if (props) {
    requestData = props
  } else {
    requestData.pagination = pagination.value
  }
  if (tokenStore.userPermissionGet('Get User List')) {
    get({
      url: 'core/user/',
      params: {
        search: search.value,
        page: requestData.pagination.page,
        max_page: requestData.pagination.rowsPerPage,
      }
    }).then(res => {
      rows.value = res.results
      rowsCount.value = res.count
    }).catch(err => {
      return Promise.reject(err)
    })
    pagination.value = requestData.pagination
  }
}

function PageChanged(e) {
  console.log('pageChange', e)
}

onMounted(() => {
  onRequest()
})


watch(() => $q.dark.isActive, val => {
  CardBackground.value = val? '#121212' : '#ffffff'
})


watch(() => pagination.value, val => {
  console.log('watch', val.sortBy)
})


watch(() => token.value, val => {
  if (val === '') {
    rows.value = []
    rowsCount.value = 0
  } else {
    onRequest()
  }
})


</script>
