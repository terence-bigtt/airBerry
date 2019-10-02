<template>
  <card>
    <b-form>
      <b-form-group
        label-cols="3"
        label="Telemetry"
        label-class="font-weight-bold pt-0"
        class="mb-0"
      >
        <label>Delay (s)</label>
        <b-form-input
          type="number"
          v-model="settings.period_s"/>

      </b-form-group>

      <b-form-group
        label-cols="3"
        label="Persistance"
        label-class="font-weight-bold pt-0"
        class="mb-0"
      >
        <label>Url</label>
        <b-form-input
          v-model="settings.url"/>
        <label>Token</label>
        <b-form-input
          v-model="settings.token"/>
        <label>Local buffer size</label>
        <b-form-input
          v-model="settings.data_buffer" type="number"/>
      </b-form-group>
      <b-button v-on:click="onSubmit" variant="primary">Submit</b-button>
      <b-button v-on:click="onReset" variant="danger">Reset</b-button>
    </b-form>
  </card>
</template>

<script>
    import _ from 'lodash'
    import axios from "axios"

    const defaultSettings = {
        period_s: null,
        url: null,
        token: null,
        data_buffer: null
    }
    export default {
        name: "Admin",
        data() {
            return {
                rootApi: process.env.VUE_APP_ROOT_API,
                settings: {}
            }
        },
        created() {
            this.loadSettings()
        },
        methods: {
            loadSettings() {
                let vm = this
                axios.get(this.rootApi + "/configuration").then((resp) => {
                    let conf = resp.data
                    console.log(conf)
                    vm.$set(vm, 'settings', conf.data)
                })
            },
            onSubmit() {
                let vm = this
                axios.post(this.rootApi + "/configuration", this.settings).then(function(resp){vm.loadSettings()})

            },
            onReset() {
                this.settings = _.clone(defaultSettings)
            }
        }
    }
</script>

<style scoped>

</style>
