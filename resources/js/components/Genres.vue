<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Genre</h3>
                <el-row>
                    <el-col :span="12">
                        <span>Genre Name</span>
                        <el-input placeholder="Genre Name" v-model="genre"></el-input>
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
                        <button @click="addNewGenre" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-table
                :data="genres"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="name"
                    label="Genre"
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
                    <el-button @click="deleteGenre(scope.$index, scope.row)" type="text" size="small"><i class="fa fa-trash"></i></el-button>
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
                        <span>Genre Name</span>
                        <el-input placeholder="Genre Name" v-model="editedGenre.name"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="editedGenre.slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <span>Description</span>
                        <el-input
                                type="textarea"
                                :rows="2"
                                placeholder="Description"
                                v-model="editedGenre.description">
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
        name: "Genres",
        mounted: function() {
            this.getAllJson();
        },
        data: function() {
            return {
                genre: '',
                description: '',
                slug: '',
                editedGenre: {},
                genres: [],
                dialogVisible: false
            }
        },
        methods: {
            addNewGenre() {
                let $this = this;
                let params = {};
                params.genre = this.genre;
                params.description = this.description;
                params.slug = this.slug;
                Axios.post('/dashboard/genre', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.clearForm();
                    });
            },
            getAllJson() {
                let $this = this;
                Axios.get('/dashboard/genre', {})
                    .then(function(response){
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.genres = data.genres;
            },
            clearForm() {
                this.genre = '';
                this.slug = '';
                this.description = '';
            },
            edit(index, row) {
                this.dialogVisible = true;
                this.editedGenre = row;
            },
            deleteGenre(index, row) {
                let $this = this;
                let id = _.get(row, 'id', '');
                if(confirm('are you sure?')) {
                    Axios.delete('/dashboard/genre/' + id)
                        .then(function(response){
                            $this.setFromJson(response.data);
                        });
                }
            },
            save() {
                let $this = this;
                let params = this.editedGenre;
                Axios.post('/dashboard/genre/edit', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.dialogVisible = false;
                        $this.editedGenre = {};
                    });
            }
        }
    }
</script>

<style scoped>
    .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>