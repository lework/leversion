<template>
  <div class="home">
    <div class="header">
      <div class="container">
        <span class="title">LE-Version</span>
      </div>
    </div>
    <div class="main">
      <div class="search">
        <a-input-search placeholder="输入仓库名称,类别"
                        v-model="search_text"
                        @search="onSearch"
                        enterButton="搜索..." />
        <div class="tips">
          <strong :style="{ marginRight: 8 }">常用类别:</strong>
          <template v-for=" tag in tags">
            <a-tag :key="tag"
                   @click="tagChange(tag)">
              {{tag}}
            </a-tag>
          </template>
        </div>

      </div>
      <div class="content">
        <!-- <a-divider orientation="left">项目列表</a-divider> -->
        <a-list itemLayout="horizontal"
                :pagination="pagination"
                :dataSource="listData">
          <div slot="footer"><b>更新时间: </b>{{ updated_at }}</div>
          <a-list-item slot="renderItem"
                       slot-scope="item, index"
                       key="item.title">
            <a-list-item-meta>
              <div slot="description">
                托管: <a-tag color="#2db7f5">{{ item.hosting }}</a-tag>
                类型: <a-tag color="#2db7f5">{{ item.type }}</a-tag>
                版本: <a-tag color="#108ee9">{{ item.tag_name || item.name }}</a-tag>
                创建时间: <a-tag color="green">{{ item.created_at || "Null"  }}</a-tag>
              </div>
              <a slot="title"
                 class="list-title"
                 :href="item.repo_url">{{item.project}}</a>
            </a-list-item-meta>
          </a-list-item>
        </a-list>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'home',
  data () {
    return {
      tags: ['Container', 'Monitor', 'Log', 'Orchestration', 'Discovery', 'Proxy', 'ServiceMesh', 'Network'],
      listData: [],
      updated_at: '',
      search_text: '',
      pagination: {
        onChange: (page) => {
          console.log(page)
        },
        pageSize: 10
      }
    }
  },
  watch: {
  },
  methods: {
    tagChange (value) {
      this.search_text = value
      this._getData(value)
    },
    onSearch (value) {
      if (typeof value === 'undefined' || value === null || value === '') {
        this._getData()
      } else {
        this._getData(value)
      }
    },
    _getData (search = '') {
      this.$axios.get('static/data/data.json').then((rep) => {
        this.updated_at = rep.data['updated_at']
        this.listData = rep.data['data']
        if (search !== '') {
          for (let i = 0; i < this.listData.length; i++) {
            if (this.listData[i]['type'].toLowerCase().indexOf(search.toLowerCase()) === -1 && this.listData[i]['project'].toLowerCase().indexOf(search.toLowerCase()) === -1) {
              this.listData.splice(i--, 1)
            }
          }
        }
      })
    }
  },
  mounted () {
    this._getData()
  }
}
</script>

<style scoped>
.home {
  width: 100%;
  height: 100%;
}
.header {
  z-index: 100;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 80px;
  line-height: 80px;
  background: #fff;
}
.container {
  height: 100%;
  width: 1140px;
  margin: 0 auto;
  padding: 0 10px;
  border-bottom: 1px solid #dcdfe6;
}

.title {
  color: #409eff;
  font-size: 26px;
  font-weight: 500;
  font-family: "微软雅黑";
}

.list-title {
  font-size: 16px;
  font-weight: bolder;
  font-family: "微软雅黑";
}

.main {
  position: relative;
  width: 1140px;
  height: -webkit-calc(100% - 80px);
  height: -moz-calc(100% - 80px);
  height: calc(100% - 80px);
  margin: 0 auto;
  padding: 10px 0;
  top: 80px;
}
.search {
  width: 600px;
  margin: 0 auto;
  text-align: center;
  padding-top: 50px;
}
.content {
  width: 100%;
  padding: 50px 80px 20px 80px;
}
.tips {
  margin-top: 10px;
}
</style>
