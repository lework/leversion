<template>
  <div class="home">
    <div class="header">
      <div class="container">
        <span class="title">LE-Version</span>
      </div>
    </div>
    <div class="main">
      <a-back-top />
      <div class="search">
        <a-input-search placeholder="输入项目名称,类别"
                        v-model="search_text"
                        @search="onSearch"
                        enterButton="搜索..." />
        <div class="tips">
          <strong :style="{ marginRight: 8 }">常用类别:</strong>
          <template v-for=" tag in tags">
            <a-tag :key="tag"
                   class="tips-tag"
                   @click="tagChange(tag)">
              {{tag}}
            </a-tag>
          </template>
        </div>

      </div>
      <div class="content">
        <!-- <a-divider orientation="left">项目列表</a-divider> -->
        <a-spin :spinning="spinning">
          <a-list itemLayout="horizontal"
                  :pagination="pagination"
                  :dataSource="listData">
            <div slot="header"><b>更新时间: </b>{{ updated_at.toLocaleString() }} <b> 统计数目: </b>{{ total }} </div>
            <a-list-item slot="renderItem"
                         slot-scope="item, index"
                         key="item.title">
              <a-list-item-meta>
                <div slot="description">
                  托管: <a-tag color="#8CD790">{{ item.hosting }}</a-tag>
                  类别: <a-tag color="#2db7f5"
                         @click="tagChange(item.type)">{{ item.type }}</a-tag>
                  版本: <a-tag color="#108ee9"
                         @click="tagClick(item.project, item.body)">{{ item.name || item.tag_name }}</a-tag>
                  创建时间: <a-tag color="#F17F42">{{ item.created_at || "None"  }}</a-tag>
                  <div class="version-info"
                       v-if="item.project === project">
                    <a-divider orientation="left">
                      <a target="_blank"
                         style="font-size: 20px;"
                         :href="item.html_url">{{ item.name || item.tag_name }}</a></a-divider>
                    <div v-html="readmeContent">
                    </div>
                  </div>
                </div>
                <a slot="title"
                   class="list-title"
                   target="_blank"
                   :href="item.repo_url">{{ item.project[0].toUpperCase() + item.project.slice(1) }}</a>
              </a-list-item-meta>
            </a-list-item>
          </a-list>
        </a-spin>
      </div>
    </div>
  </div>
</template>

<script>
import marked from 'marked'
export default {
  name: 'home',
  data () {
    return {
      tags: ['Container', 'Monitor', 'Log', 'Orchestration', 'Discovery', 'Proxy', 'ServiceMesh', 'Network', 'Ci', 'versionControl', 'db', 'kv-Store'],
      listData: [],
      updated_at: '',
      total: '',
      search_text: '',
      pagination: {
        pageSize: 10
      },
      readmeContent: '',
      project: '',
      spinning: true
    }
  },
  watch: {
  },
  methods: {
    tagClick (project, data) {
      if (this.project !== '' && this.project === project) {
        this.project = ''
        this.readmeContent = ''
        return
      }
      this.project = project
      this.readmeContent = marked(data || 'None')
    },
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
        this.listData = rep.data['data']
        this.total = rep.data['total']
        this.updated_at = rep.data['updated_at']
        if (search !== '') {
          for (let i = 0; i < this.listData.length; i++) {
            if (this.listData[i]['type'].toLowerCase().indexOf(search.toLowerCase()) === -1 && this.listData[i]['project'].toLowerCase().indexOf(search.toLowerCase()) === -1) {
              this.listData.splice(i--, 1)
            }
          }
          if (this.listData.length === 0) {
            this._getGithub(search)
          }
        }
        this.spinning = false
      }).catch((e) => {
        console.log(e)
      })
    },
    _getGithub (repo) {
      let repoUrl = 'https://api.github.com/repos/' + repo + '/releases/latest'
      this.$axios.get(repoUrl).then((res) => {
        let data = {
          'name': res.data['name'],
          'tag_name': res.data['tag_name'],
          'html_url': res.data['html_url'],
          'repo_url': 'https://github.com/' + repo,
          'body': res.data['body'],
          'created_at': res.data['created_at'],
          'project': repo,
          'hosting': 'github',
          'type': 'None'
        }
        this.listData = [data]
        this.total = this.listData.length
        this.updated_at = new Date()
      }).catch((e) => {
        console.log(e)
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
.tips-tag {
  margin-bottom: 5px;
}
.version-info {
  margin: 20px;
  color: black;
}
</style>
