<template>
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
                                :key="category.value"
                                :label="category.label"
                                :value="category.value">
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
                                v-for="runner in runners"
                                :key="runner.value"
                                :label="runner.label"
                                :value="runner.value">
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
                                :key="game.value"
                                :label="game.label"
                                :value="game.value">
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
                                :key="platform.value"
                                :label="platform.label"
                                :value="platform.value">
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
                                v-for="event in events"
                                :key="event.value"
                                :label="event.label"
                                :value="event.value">
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
            </el-row>
            <el-row>
                <el-col :span="12">
                    <button @click="addNewRun" class="btn btn-primary">Add</button>
                </el-col>
            </el-row>

        </div>
    </div>
</template>

<script>
    import Axios from 'axios'
    export default {
        name: "Runs",
        mounted: function() {
           // get the category options
        },
        data: function() {
            return {
                categories: [],
                categoryOptions: [],
                runners: [],
                runnerOptions: [],
                game: '',
                gameOptions: [],
                platform: '',
                platformOptions: [],
                event: '',
                events: [],
                time: null,
                twitchId:'',
                youtubeId:'',
            }
        },
        methods: {
            getCategories() {

            },
            addNewRun() {
                let params = {};
                params.categories = this.categories;
                params.runners = this.runners;
                params.game = this.game;
                params.platform = this.platform;
                params.event = this.event;
                params.time = this.time;
                params.twitchId = this.twitchId;
                params.youtubeId = this.youtubeId;

                Axios.post('/dashboard/run', params)
                    .then(function(response){
                       console.log(response);
                    });
            }
        }
    }
</script>

<style scoped>
 .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>