<template>
    
    <span :style="{ color: isAddMode ? '#000' : 'gray', 'margin-right': '8px' }" @click="toggleMode('add')">添加键</span>
    <span :style="{ color: !isAddMode ? '#000' : 'gray' }" @click="toggleMode('delete')">删除键</span>
    <div style="display: flex; margin-top: 8px; gap: 16px; align-items:center">
        <!-- {{ items }} -->
        <v-text-field v-model="newItemKey" label="键名" style="max-width: 250px;" density="compact"
            prepend-inner-icon="mdi-alpha-k" variant="solo-filled" flat hide-details single-line
            rounded="md"></v-text-field>
        <v-select v-if="isAddMode" hint="类型" style="max-width: 150px;" rounded="md" density="compact" v-model="newItemType" :items="typeOptions"
            prepend-inner-icon="mdi-alpha-t" variant="solo-filled" flat hide-details single-line>
        </v-select>
        <v-btn @click="apply" variant="tonal">
            确定
        </v-btn>
        <small color="error">{{ error }}</small>
    </div>
</template>

<script>
export default {
    name: 'ObjectConfigItem',
    props: {
        object: {
            type: Object,
            default: () => ({}),
        },
        metadata: {
            type: Object,
            default: () => ({}),
        },
    },
    data() {
        return {
            items: this.object,
            metadata: this.metadata,
            newItemKey: '',
            newItemType: 'string',
            typeOptions: [
                'string',
                'int',
                'float',
                'text',
                'bool',
                'list',
                'object',
            ],
            error: '',
            isAddMode: true, // 默认模式为添加键

            defaultValues: {
                string: '',
                int: 0,
                float: 0.0,
                text: '',
                bool: false,
                list: [],
                object: {},
            },
        };
    },
    methods: {
        toggleMode(mode) {
            this.isAddMode = (mode === 'add');
            this.newItemKey = '';
            this.error = '';
        },
        apply() {
            if (this.newItemKey === '') {
                this.error = '键不能为空';
                return;
            }
            if (this.isAddMode) {
                if (this.items[this.newItemKey]) {
                    this.error = '键已存在';
                    return;
                }
                if (!this.newItemType) {
                    this.error = '请选择类型';
                    return;
                }
                this.items[this.newItemKey] = this.defaultValues[this.newItemType];
                this.metadata[this.newItemKey] = {
                    type: this.newItemType,
                    description: this.newItemKey,
                };
                this.newItemType = 'string';
            } else {
                delete this.items[this.newItemKey];
                delete this.metadata[this.newItemKey];
            }
            this.newItemKey = '';
            this.error = '';
        },
    },
};
</script>

<style></style>