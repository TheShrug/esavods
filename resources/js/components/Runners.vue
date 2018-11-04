<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Runner</h3>
                <el-row>
                    <el-col :span="12">
                        <span>Runner Name</span>
                        <el-input placeholder="Runner Name" v-model="runner"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="slug"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Twitch</span>
                        <el-input placeholder="Twitch" v-model="twitch"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Twitter</span>
                        <el-input placeholder="Twitter" v-model="twitter"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Youtube</span>
                        <el-input placeholder="Youtube" v-model="youtube"></el-input>
                    </el-col>

                </el-row>
                <el-row>
                    <el-col :span="12">
                        <button @click="addNewRunner" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-table
                :data="runners"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="name"
                    label="Runner"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="slug"
                    label="Slug"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="twitch"
                    label="Twitch"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="twitter"
                    label="Twitter"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="youtube"
                    label="Youtube"
                    width="">
            </el-table-column>
            <el-table-column
                    fixed="right"
                    label="Operations"
                    width="120"
                    prop="id">
                <template slot-scope="scope">
                    <el-button @click="edit(scope.$index, scope.row)" type="text" size="small">Edit</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-dialog
                title="Edit"
                :visible.sync="dialogVisible"
                width="30%"
        >
            <span>
                <el-row>
                    <el-col :span="12">
                        <span>Runner Name</span>
                        <el-input placeholder="Runner Name" v-model="editedRunner.name"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="editedRunner.slug" label="test"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Twitch</span>
                        <el-input placeholder="Twitch" v-model="editedRunner.twitch"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Twitter</span>
                        <el-input placeholder="Twitter" v-model="editedRunner.twitter"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Youtube</span>
                        <el-input placeholder="Youtube" v-model="editedRunner.youtube"></el-input>
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
        name: "Runners",
        mounted: function() {
            this.getAllJson();
        },
        data: function() {
            return {
                runner: '',
                slug: '',
                twitch: '',
                twitter: '',
                youtube: '',
                editedRunner: {},
                runners: [],
                dialogVisible: false
            }
        },
        methods: {
            addNewRunner() {
                let $this = this;
                let params = {};
                params.runner = this.runner;
                params.twitch = this.twitch;
                params.twitter = this.twitter;
                params.youtube = this.youtube;
                params.slug = this.slug;
                Axios.post('/dashboard/runner', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.clearForm();
                    });
            },
            getAllJson() {
                let $this = this;
                Axios.get('/dashboard/runner', {})
                    .then(function(response){
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.runners = data.runners;
            },
            clearForm() {
                this.runner = '';
                this.slug = '';
                this.twitch = '';
                this.twitter = '';
                this.youtube = '';
            },
            edit(index, row) {
                this.dialogVisible = true;
                this.editedRunner = row;
            },
            save() {
                let $this = this;
                let params = this.editedRunner;
                Axios.post('/dashboard/runner/edit', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.dialogVisible = false;
                        $this.editedRunner = {};
                    });
            }
        }
    }
</script>

<style scoped>
    .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>