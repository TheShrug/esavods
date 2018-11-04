<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Run</h3>
                <el-row>
                    <el-col :span="12">
                        <el-select
                                v-model="categories"
                                multiple
                                filterable
                                allow-create
                                default-first-option
                                placeholder="Choose categories"
                                >
                            <el-option
                                    v-for="category in categoryOptions"
                                    :key="category.id"
                                    :label="category.name"
                                    :value="category.name">
                            </el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="12">
                        <el-select
                                v-model="runners"
                                multiple
                                filterable
                                allow-create
                                default-first-option
                                placeholder="Choose runners"
                                >
                            <el-option
                                    v-for="runner in runnerOptions"
                                    :key="runner.id"
                                    :label="runner.name"
                                    :value="runner.name">
                            </el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="12">
                        <el-select
                                v-model="game"
                                filterable
                                allow-create
                                default-first-option
                                placeholder="Choose game"
                                >
                            <el-option
                                    v-for="game in gameOptions"
                                    :key="game.id"
                                    :label="game.name"
                                    :value="game.name">
                            </el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="12">
                        <el-select
                                v-model="platform"
                                filterable
                                allow-create
                                default-first-option
                                placeholder="Choose platform"
                        >
                            <el-option
                                    v-for="platform in platformOptions"
                                    :key="platform.id"
                                    :label="platform.name"
                                    :value="platform.name">
                            </el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="12">
                        <el-select
                                v-model="event"
                                filterable
                                allow-create
                                default-first-option
                                placeholder="Choose Event"
                        >
                            <el-option
                                    v-for="event in eventOptions"
                                    :key="event.id"
                                    :label="event.name"
                                    :value="event.name">
                            </el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="12">
                        <el-input v-model="time" :controls="false">
                            <template slot="prepend">Run time</template>
                        </el-input>
                    </el-col>
                    <el-col :span="12">
                        <el-input placeholder="Twitch Id" v-model="twitchId"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <el-input placeholder="Youtube Id" v-model="youtubeId" ></el-input>
                    </el-col>
                    <el-col :span="12">
                        <el-input placeholder="Youtube Id" v-model="runCategory" ></el-input>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <button @click="addNewRun" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-table
                :data="runs"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="address"
                    label="Address"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="zip"
                    label="Zip"
                    width="">
            </el-table-column>
            <el-table-column
                    fixed="right"
                    label="Operations"
                    width="120">
                <template slot-scope="scope">
                    <el-button type="text" size="small">Detail</el-button>
                    <el-button type="text" size="small">Edit</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script>
    import Axios from 'axios'
    export default {
        name: "Runs",
        mounted: function() {
           this.getAllJson();
        },
        data: function() {
            return {
                categories: [],
                categoryOptions: [],
                runCategory: '',
                runners: [],
                runnerOptions: [],
                game: '',
                gameOptions: [],
                platform: '',
                platformOptions: [],
                event: '',
                eventOptions: [],
                time: null,
                twitchId:'',
                youtubeId:'',
                runs: []
            }
        },
        methods: {
            addNewRun() {
                let $this = this;
                let params = {};
                params.categories = this.categories;
                params.runners = this.runners;
                params.game = this.game;
                params.platform = this.platform;
                params.event = this.event;
                params.time = this.time;
                params.twitchId = this.twitchId;
                params.youtubeId = this.youtubeId;
                params.runCategory = this.runCategory;

                Axios.post('/dashboard/run', params)
                    .then(function(response){
                       $this.setFromJson(response.data);
                       $this.clearForm();
                    });
            },
            getAllJson() {
                let $this = this;
                Axios.get('/dashboard/all', {})
                    .then(function(response){
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.categoryOptions = data.categories;
                this.runnerOptions = data.runners;
                this.eventOptions = data.events;
                this.gameOptions = data.games;
                this.platformOptions = data.platforms;
                this.runs = data.runs;
            },
            clearForm() {
                this.categories = [];
                this.runners = [];
                this.event = '';
                this.game = '';
                this.platform = '';
                this.twitchId = '';
                this.youtubeId = '';
                this.time = '';
                this.runCategory = '';
            }
        }
    }
</script>

<style scoped>
 .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>