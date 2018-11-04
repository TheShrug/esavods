<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Platform</h3>
                <el-row>
                    <el-col :span="12">
                        <span>Platform Name</span>
                        <el-input placeholder="Platform Name" v-model="platform"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <span>Description</span>
                        <el-input
                                type="textarea"
                                :rows="4"
                                placeholder="Description"
                                v-model="description">
                        </el-input>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <button @click="addNewPlatform" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-table
                :data="platforms"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="name"
                    label="Platform"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="slug"
                    label="Slug"
                    width="">
            </el-table-column>
            <el-table-column
                    prop="description"
                    label="Description"
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
                        <span>Platform Name</span>
                        <el-input placeholder="Platform Name" v-model="editedPlatform.name"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="editedPlatform.slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <span>Description</span>
                        <el-input
                                type="textarea"
                                :rows="2"
                                placeholder="Description"
                                v-model="editedPlatform.description">
                        </el-input>
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
        name: "Platforms",
        mounted: function() {
            this.getAllJson();
        },
        data: function() {
            return {
                platform: '',
                description: '',
                slug: '',
                editedPlatform: {},
                platforms: [],
                dialogVisible: false
            }
        },
        methods: {
            addNewPlatform() {
                let $this = this;
                let params = {};
                params.platform = this.platform;
                params.description = this.description;
                params.slug = this.slug;
                Axios.post('/dashboard/platform', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.clearForm();
                    });
            },
            getAllJson() {
                let $this = this;
                Axios.get('/dashboard/platform', {})
                    .then(function(response){
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.platforms = data.platforms;
            },
            clearForm() {
                this.platform = '';
                this.slug = '';
                this.description = '';
            },
            edit(index, row) {
                this.dialogVisible = true;
                this.editedPlatform = row;
            },
            save() {
                let $this = this;
                let params = this.editedPlatform;
                Axios.post('/dashboard/platform/edit', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.dialogVisible = false;
                        $this.editedPlatform = {};
                    });
            }
        }
    }
</script>

<style scoped>
    .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>