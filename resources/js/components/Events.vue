<template>
    <div>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title">New Event</h3>
                <el-row>
                    <el-col :span="12">
                        <span>Event Name</span>
                        <el-input placeholder="Event Name" v-model="event"></el-input>
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
                        <button @click="addNewEvent" class="btn btn-primary">Add</button>
                    </el-col>
                </el-row>
            </div>
        </div>
        <el-table
                :data="events"
                style="width: 100%"
                size="small">
            <el-table-column
                    prop="name"
                    label="Event"
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
                        <span>Event Name</span>
                        <el-input placeholder="Event Name" v-model="editedEvent.name"></el-input>
                    </el-col>
                    <el-col :span="12">
                        <span>Slug</span>
                        <el-input placeholder="Slug" v-model="editedEvent.slug"></el-input>
                    </el-col>
                    <el-col :span="24">
                        <span>Description</span>
                        <el-input
                                type="textarea"
                                :rows="2"
                                placeholder="Description"
                                v-model="editedEvent.description">
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
        name: "Events",
        mounted: function() {
            this.getAllJson();
        },
        data: function() {
            return {
                event: '',
                description: '',
                slug: '',
                editedEvent: {},
                events: [],
                dialogVisible: false
            }
        },
        methods: {
            addNewEvent() {
                let $this = this;
                let params = {};
                params.event = this.event;
                params.description = this.description;
                params.slug = this.slug;
                Axios.post('/dashboard/event', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.clearForm();
                    });
            },
            getAllJson() {
                let $this = this;
                Axios.get('/dashboard/event', {})
                    .then(function(response){
                        $this.setFromJson(response.data);
                    });
            },
            setFromJson(data) {
                this.events = data.events;
            },
            clearForm() {
                this.event = '';
                this.slug = '';
                this.description = '';
            },
            edit(index, row) {
                this.dialogVisible = true;
                this.editedEvent = row;
            },
            save() {
                let $this = this;
                let params = this.editedEvent;
                Axios.post('/dashboard/event/edit', params)
                    .then(function(response){
                        $this.setFromJson(response.data);
                        $this.dialogVisible = false;
                        $this.editedEvent = {};
                    });
            }
        }
    }
</script>

<style scoped>
    .el-col {padding: 0 15px;margin-bottom: 15px;}
</style>