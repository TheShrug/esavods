<template>
    <div>
        <div class="card">
            <div class="card-body">
                <el-upload
                        class="upload-demo"
                        ref="upload"
                        action="/dashboard/runs/upload"
                        :headers="uploadHeaders"
                        :auto-upload="false">
                    <el-button slot="trigger" size="small" type="primary">select file</el-button>
                    <el-button style="margin-left: 10px;" size="small" type="success" @click="uploadFile">upload to server</el-button>
                    <div class="el-upload__tip" slot="tip">jpg/png files with a size less than 500kb</div>
                </el-upload>
                <h3 class="card-title">New Run</h3>
                <el-row>
                    <el-col :span="6">
                        <div>Game</div>
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
                    <el-col :span="6">
                        <span>Category</span>
                        <el-input placeholder="Category" v-model="runCategory" ></el-input>
                    </el-col>
                    <el-col :span="6">
                        <div>Runners</div>
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
                    <el-col :span="6">
                        <div>Platform</div>
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
                </el-row>
                <el-row>
                    <el-col :span="6">
                        <div>Event</div>
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
                    <el-col :span="6">
                        <span>Time</span>
                        <el-input v-model="time" :controls="false" v-on:blur="calculateSeconds">
                            <template slot="prepend">Run time</template>
                        </el-input>
                    </el-col>
                    <el-col :span="6">
                        <span>Twitch Vod ID</span>
                        <el-input placeholder="Twitch Id" v-model="twitchId"></el-input>
                    </el-col>
                    <el-col :span="6">
                        <span>Youtube Vod ID</span>
                        <el-input placeholder="Youtube Id" v-model="youtubeId" ></el-input>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="6">
                        <span>Date</span>
                        <el-date-picker
                                v-model="datetime"
                                type="datetime"
                                placeholder="Select date and time"
                                value-format="yyyy-MM-dd HH:mm:ss"
                        >
                        </el-date-picker>
                    </el-col>
                    <el-col :span="6">
                        <div>Categories</div>
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
                    <el-col :span="6">
                        <div>Genres</div>
                        <el-select
                                v-model="genres"
                                multiple
                                filterable
                                allow-create
                                default-first-option
                                placeholder="Choose genres"
                        >
                            <el-option
                                    v-for="genre in genreOptions"
                                    :key="genre.id"
                                    :label="genre.name"
                                    :value="genre.name">
                            </el-option>
                        </el-select>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <button @click="addNewRun" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-pagination
                layout="prev, pager, next"
                :total="pagination.total"
                :current-page="pagination.current_page"
                :page-size="pagination.per_page"
                @current-change="changedPage($event)">
        </el-pagination>
        <el-table
                :data="runs"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="id"
                    label="ID"
                    width=""
                    sortable>
            </el-table-column>
            <el-table-column
                    prop="run_date"
                    label="Date"
                    width=""
                    sortable>
            </el-table-column>
            <el-table-column
                    prop="game.name"
                    label="Game"
                    width=""
                    sortable>
            </el-table-column>
            <el-table-column
                    prop="platform.name"
                    label="Platform"
                    width=""
                    sortable>
            </el-table-column>
            <el-table-column
                    prop="event.name"
                    label="Event"
                    width=""
                    sortable>
            </el-table-column>
            <el-table-column
                    prop="time"
                    label="Time"
                    width=""
                    sortable>
            </el-table-column>
            <el-table-column
                    prop="twitch_vod_id"
                    label="Twitch Vod"
                    width="">
            </el-table-column>
            <el-table-column
                prop="youtube_vod_id"
                label="Youtube Vod"
                width="">
            </el-table-column>
            <el-table-column
                    prop="category"
                    label="Category"
                    width="">
            </el-table-column>
            <el-table-column
                    fixed="right"
                    label="Edit"
                    width="80">
                <template slot-scope="scope">
                    <el-button @click="edit(scope.$index, scope.row)" type="text" size="small">Edit</el-button>
                    <el-button @click="deleteRun(scope.$index, scope.row)" type="text" size="small"><i class="fa fa-trash"></i></el-button>
                </template>


            </el-table-column>
        </el-table>
        <el-pagination
                layout="prev, pager, next"
                :total="pagination.total"
                :current-page="pagination.current_page"
                :page-size="pagination.per_page"
                @current-change="changedPage($event)">
        </el-pagination>
        <el-dialog
                title="Edit"
                :visible.sync="dialogVisible"
                width="30%"
        >
            <span>
                <el-row>
                    <el-col :span="12">
                        <div>Categories</div>
                        <el-select
                                v-model="editedRun.categories"
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
                        <div>Runners</div>
                        <el-select
                                v-model="editedRun.runners"
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
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <div>Game</div>
                        <el-select
                                v-model="editedRun.game"
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
                        <div>Platform</div>
                        <el-select
                                v-model="editedRun.platform"
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
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <div>Event</div>
                        <el-select
                                v-model="editedRun.event"
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
                        <span>Time</span>
                        <el-input v-model="editedRun.time" :controls="false">
                            <template slot="prepend">Run time</template>
                        </el-input>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <span>Twitch Vod ID</span>
                        <el-input placeholder="Twitch Id" v-model="editedRun.twitchId"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Youtube Vod ID</span>
                        <el-input placeholder="Youtube Id" v-model="editedRun.youtubeId" ></el-input>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <span>Category</span>
                        <el-input placeholder="Category" v-model="editedRun.runCategory" ></el-input>
                    </el-col>
                      <el-col :span="12">
                        <span>Date</span>
                        <el-date-picker
                                v-model="editedRun.datetime"
                                type="datetime"
                                placeholder="Select date and time"
                                value-format="yyyy-MM-dd HH:mm:ss">
                        </el-date-picker>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <div>Genres</div>
                        <el-select
                                v-model="editedRun.genres"
                                multiple
                                filterable
                                allow-create
                                default-first-option
                                placeholder="Choose genres"
                        >
                            <el-option
                                    v-for="genre in genreOptions"
                                    :key="genre.id"
                                    :label="genre.name"
                                    :value="genre.name">
                            </el-option>
                        </el-select>
                    </el-col>
                </el-row>
            </span>
            <span slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="save()">Confirm</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    import Axios from 'axios'
    export default {
        name: "Runs",
        mounted: function() {
            this.getXsrf();

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
                datetime: '',
                runs: [],
                dialogVisible: false,
                editedRun: {},
                genres: [],
                genreOptions: [],
                pagination:  {
                    current_page: 1,
                    last_page: 0,
                    per_page: 0,
                    total: 0
                },
                uploadHeaders : {
                    "X-CSRF-TOKEN": ''
                },
            }
        },
        methods: {
            getXsrf() {
              let token = document.head.querySelector("meta[name=csrf-token]").content;
              this.uploadHeaders["X-CSRF-TOKEN"] = token;
            },
            uploadFile() {
              this.$refs.upload.submit();
            },
            changedPage(newPage) {
                let $this = this;
                $this.pagination.current_page = newPage;
                $this.getPaginatedRuns();
            },
            getPaginatedRuns() {
                let $this = this;
                Axios.get('/dashboard/runs', {
                    params: {page: $this.pagination.current_page}
                }).then(function(response){
                        $this.setRuns(response.data);
                });
            },
            setRuns(data) {
                let $this = this;
                $this.runs = data.data;
            },
            addNewRun() {
                let $this = this;
                let params = {};
                params.categories = this.categories;
                params.genres = this.genres;
                params.runners = this.runners;
                params.game = this.game;
                params.platform = this.platform;
                params.event = this.event;
                params.time = this.time;
                params.twitchId = this.twitchId;
                params.youtubeId = this.youtubeId;
                params.runCategory = this.runCategory;
                params.datetime = this.datetime;

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
                this.genreOptions = data.genres;
                this.runs = data.runs.data;
                this.pagination.current_page = data.runs.current_page;
                this.pagination.last_page = data.runs.last_page;
                this.pagination.total = data.runs.total;
                this.pagination.per_page = data.runs.per_page;
            },
            clearForm() {
                this.categories = [];
                this.runners = [];
                this.game = '';
                this.platform = '';
                this.twitchId = '';
                this.youtubeId = '';
                this.time = '';
                this.runCategory = '';
                this.genres = [];
            },
            edit(index, row) {
                let $this = this;
                this.dialogVisible = true;

                this.editedRun = {
                    id: _.get(row, 'id', ''),
                    categories: [],
                    genres: [],
                    runCategory: _.get(row, 'category', ''),
                    runners: [],
                    genres: [],
                    game: _.get(row, 'game.name', ''),
                    platform: _.get(row, 'platform.name', ''),
                    event: _.get(row, 'event.name', ''),
                    time: _.get(row, 'time', ''),
                    twitchId: _.get(row, 'twitch_vod_id', ''),
                    youtubeId: _.get(row, 'youtube_vod_id', ''),
                    datetime: _.get(row, 'run_date', ''),
                };

                row.categories.forEach(function(category) {
                    $this.editedRun.categories.push(category.name)
                });
                row.runners.forEach(function(runner) {
                    $this.editedRun.runners.push(runner.name)
                });
                row.genres.forEach(function(genre) {
                    $this.editedRun.genres.push(genre.name)
                });
            },
            deleteRun(index, row) {
                let $this = this;
                let id = _.get(row, 'id', '');
                if(confirm('are you sure?')) {
                    Axios.delete('/dashboard/run/' + id)
                        .then(function(response){
                            $this.setFromJson(response.data);
                        });
                }
            },
            save() {
                let $this = this;
                let params = this.editedRun;
                Axios.post('/dashboard/run/edit', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.dialogVisible = false;
                    });
            },
            calculateSeconds() {
                let timeSegments = this.time.split(':');
                let seconds = 0;
                if(timeSegments.length === 3) {
                    seconds += parseInt(timeSegments[0]) * 60 * 60;
                    seconds += parseInt(timeSegments[1]) * 60;
                    seconds += parseInt(timeSegments[2]);
                } else {
                    seconds = this.time;
                }
                this.time = seconds;
            }
        }
    }
</script>

<style scoped>
 .el-col {padding: 0 15px;margin-bottom: 15px;}
    .card-body span {display: block;}
</style>