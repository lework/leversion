<template>
  <div class="home">
    <div class="header">
      <div class="container">
        <span class="title"><a href="#">LE-Version</a></span>
        <span class="title-desc"> 列出开源软件的当前版本</span>
      </div>
    </div>
    <div class="main">
      <a-back-top />
      <div class="search">
        <a-input-search placeholder="输入user/repo,Container"
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
            <div slot="header"><b>更新时间: </b>{{ updated_at.toLocaleString() }} <b> 统计数目: </b>{{ total }}
              <div class="header-switch">
                <a-switch checkedChildren="Shields"
                          unCheckedChildren="Shields"
                          @click="switchCheck" />
              </div>
            </div>
            <a-list-item slot="renderItem"
                         slot-scope="item, index"
                         key="item.title">
              <a-list-item-meta>
                <div slot="description">
                  托管: <a-tag color="#8CD790">{{ item.hosting }}</a-tag>
                  类别: <a-tag color="#2db7f5"
                         @click="tagChange(item.type)">{{ item.type }}</a-tag>
                  当前版本: <a-tag color="#108ee9"
                         @click="tagClick(item.project, item.body)">{{ item.name || item.tag_name }}</a-tag>
                  <a-tag color="#5bd1d7"
                         @click="lastClick(item.project, item.html_url, item.repo)">最近版本</a-tag>
                  创建时间: <a-tag color="#F17F42">{{ item.created_at || "None"  }}</a-tag>
                  <span v-if="shieldsShow">shield: </span>
                  <img v-if="shieldsShow && item.html_url.indexOf('release') !== -1"
                       alt="GitHub release (latest by date)"
                       :src="'https://img.shields.io/github/v/release/'+ item.repo">
                  <img v-if="shieldsShow && item.html_url.indexOf('commit') !== -1"
                       alt="GitHub tag (latest by date)"
                       :src="'https://img.shields.io/github/v/tag/'+ item.repo ">

                  <div class="version-info"
                       v-if="item.project === project">
                    <a-spin :spinning="versionSpinning">
                      <div v-if="showLast">
                        <a-divider orientation="left">
                          <span style="font-size: 16px;">最近10个版本</span>
                        </a-divider>
                        <a-timeline>
                          <template v-for="(last, index) in lastData">
                            <a-timeline-item :key="index">
                              <a target="_blank"
                                 :href="last.html_url">
                                {{ last.name || last.tag_name }}</a> [{{last.created_at}}]

                            </a-timeline-item>
                          </template>
                        </a-timeline>
                      </div>
                      <div v-if="showInfo">
                        <a-divider orientation="left">
                          <a target="_blank"
                             style="font-size: 20px;"
                             :href="item.html_url">{{ item.name || item.tag_name }}</a></a-divider>
                        <div v-html="readmeContent">
                        </div>
                      </div>
                    </a-spin>
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
      <div class="footer">
        <p><a href="https://github.com/lework/leversion/issues"
             target="_blank">告诉我们</a>，我们可能会把它带给您！</p>
        leversion ©2019 Created by Lework <a href="https://github.com/lework/leversion"
           target="_blank">GitHub</a>
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
      spinning: true,
      shieldsShow: false,
      timer: '',
      showInfo: false,
      showLast: false,
      versionSpinning: true,
      lastData: []
    }
  },
  watch: {
  },
  methods: {
    lastClick (project, url, repo) {
      this.versionSpinning = true
      if (this.project === project && this.showLast) {
        this.showLast = false
        this.project = ''
        return
      }
      if (this.project !== project && url.indexOf('release') !== -1) {
        let repoUrl = 'https://api.github.com/repos/' + repo + '/releases?per_page=10'
        this.$axios.get(repoUrl).then((res) => {
          this.lastData = res.data
          this.versionSpinning = false
        }).catch((e) => {
          this.$message.error('获取数据失败')
          console.log(e)
        })
      } else if (this.project !== project && url.indexOf('commit') !== -1) {
        let graphqlUrl = 'https://api.github.com/graphql'
        let postData = {
          'query': '{repository(owner: "' + repo.split('/')[0] + '", name: "' + repo.split('/')[1] + '") {refs(refPrefix: "refs/tags/", first: 10, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {edges {node {name target {commitUrl ... on Tag {tagger {date}} ... on Commit {committedDate}}}}}}}'
        }
        let token = '99510f2ccf40e496d1e97dbec9f31cb16770b884'
        let headers = { 'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'token ' + token }
        this.$axios.post(graphqlUrl, postData, { headers }).then((res) => {
          let lastTags = res.data['data']['repository']['refs']['edges']
          this.lastData = []
          for (let item in lastTags) {
            this.lastData.push({
              'tag_name': lastTags[item]['node']['name'],
              'html_url': lastTags[item]['node']['target']['commitUrl'] || '',
              'created_at': lastTags[item]['node']['target'].hasOwnProperty('tagger') ? lastTags[item]['node']['target']['tagger']['date'] : lastTags[item]['node']['target']['committedDate']
            })
          }
          this.versionSpinning = false
        }).catch((e) => {
          this.$message.error('获取数据失败')
          console.log(e)
        })
      } else {
        this.versionSpinning = false
      }

      this.project = project
      this.showLast = true
      this.showInfo = false
    },
    switchCheck (b) {
      this.spinning = true
      this.shieldsShow = b
      this.timer = setTimeout(() => {
        this.spinning = false
      }, parseInt(Math.random() * 1000 + 1000))
    },
    tagClick (project, data) {
      this.versionSpinning = true
      if (this.project === project && this.showInfo) {
        this.readmeContent = ''
        this.project = ''
        this.showInfo = false
        return
      }
      this.readmeContent = marked(data || 'None')
      this.project = project
      this.showInfo = true
      this.showLast = false
      this.versionSpinning = false
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
        this.$message.error('获取数据失败')
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
        this.$message.error('获取数据失败')
        console.log(e)
      })
    }
  },
  mounted () {
    this._getData()
  },
  beforeDestroy () {
    this.timer && clearTimeout(this.timer)
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
.title-desc {
  color: rgba(0, 0, 0, 0.45);
  margin-left: 10px;
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
.header-switch {
  float: right;
}
.footer {
  text-align: center;
  line-height: 32px;
  padding: 20px 0;
  color: rgba(0, 0, 0, 0.45);
}
</style>
