<template>
  <div class="home">
    <div class="header">
      <div class="container">
        <span class="title"><a href="./">LE-Version</a></span>
        <span class="title-desc"> 列出开源软件的当前版本</span>
      </div>
    </div>
    <div class="main">
      <a-back-top />
      <div class="search">
        <a-input-search placeholder="输入user/repo or type"
                        v-model="search_text"
                        @search="onSearch"
                        enterButton="搜索..." />
        <div class="tips">
          <strong :style="{ marginRight: 8 }">常用类别:</strong>
          <a-tag color="#df405a"
                 style="margin: auto;"
                 @click="trendClick">Trending</a-tag>
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
                  :dataSource="listData"
                  v-if="listData.length !== 0">
            <div slot="header"
                 class="list-header"><b>更新时间: </b>{{ updated_at.toLocaleString() }} <b> 统计数目: </b>{{ total }}
              <div class="header-switch">
                <a-switch v-if="listData.length !== 0"
                          checkedChildren="Shields"
                          unCheckedChildren="Shields"
                          @click="switchCheck" />
              </div>
            </div>
            <a-list-item slot="renderItem"
                         slot-scope="item, index"
                         key="item.title">
              <a-list-item-meta>
                <div slot="description">
                  <span class="tag-title">托管: </span>
                  <a-tag color="#8CD790">{{ item.hosting }}</a-tag>
                  <span class="tag-title">类别: </span>
                  <a-tag color="#2db7f5"
                         @click="tagChange(item.type)">{{ item.type }}</a-tag>
                  <span class="tag-title">当前{{ item.html_url.indexOf('release') !== -1 ? '版本' : 'Tag' }}: </span>
                  <a-tooltip placement="top"
                             :title="item.created_at">
                    <a-tag color="#108ee9"
                           @click="tagClick(item.project, item.body)">{{ item.name || item.tag_name }}</a-tag>
                  </a-tooltip>
                  <a-tooltip placement="top"
                             title="Last 10">
                    <a-tag color="#5bd1d7"
                           @click="lastClick(item.project, item.html_url, item.repo)">最近{{ item.html_url.indexOf('release') !== -1 ? '版本' : 'Tag' }}</a-tag>
                  </a-tooltip>
                  <span class="tag-title">创建时间: </span>
                  <a-tag color="#F17F42">{{ item.created_at || "None"  }}</a-tag>
                  <span v-if="shieldsShow"
                        class="tag-title">shield: </span>
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
                          <span style="font-size: 16px;">最近10个{{ item.html_url.indexOf('release') !== -1 ? '版本' : 'Tag' }}</span>
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
                             class="info-title"
                             :href="item.html_url">{{ item.name || item.tag_name }} [{{item.created_at}}]</a></a-divider>
                        <div class="repo-desc"
                             v-html="readmeContent">
                        </div>
                      </div>
                    </a-spin>
                  </div>
                </div>
                <a slot="title"
                   class="list-title"
                   target="_blank"
                   :id="item.project"
                   :href="item.repo_url">{{ item.project[0].toUpperCase() + item.project.slice(1) }}</a>
              </a-list-item-meta>
            </a-list-item>
          </a-list>
          <a-list itemLayout="horizontal"
                  :dataSource="searchData"
                  v-if="searchData.length !== 0 && listData.length === 0">
            <div slot="header"
                 v-if="!trending"
                 class="list-header">在下列中选择你的项目吧! 本次搜索到了<b>{{ searchCount }}</b>个，只显示 Star <b>TOP10</b>.
            </div>
            <div slot="header"
                 v-if="trending"
                 class="list-header">当天的Github Trending.
            </div>
            <a-list-item slot="renderItem"
                         slot-scope="item, index">
              <a-list-item-meta>
                <div slot="description">
                  {{item.description}}
                  <p />
                  <p>
                    <a-icon type="star"
                            theme="filled" /> {{item.stargazers_count}}
                    <a-icon type="fork" /> {{item.forks_count}}
                    <a-icon type="code"
                            theme="filled" /> {{item.language}}
                    <a-tooltip placement="top"
                               v-if="item.updated_at">
                      <template slot="title">
                        <span>最近更新</span>
                      </template>
                      <a-icon type="calendar"
                              theme="filled" /> {{item.updated_at}}
                    </a-tooltip>
                    <span v-if="item.currentPeriodStars">
                      <a-icon type="star"
                              theme="filled" />{{item.currentPeriodStars}} stars today</span>
                    <span @click="tagChange(item.full_name)"> [查看版本]</span>
                  </p>
                </div>

                <a slot="title"
                   class="list-title"
                   target="_blank"
                   :href="item.html_url">{{item.full_name}}</a>
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
      tags: ['Ci', 'Installer', 'Monitor', 'Log', 'Proxy', 'Discovery', 'Db', 'Pass', 'Container', 'ServiceMesh', 'Storage', 'Automation', 'Tracing', 'Network', 'VersionControl', 'Message', 'Orchestration', 'Registry', 'Gateway', 'DevOps', 'Config', 'Package', 'Kv-Store', 'Remote Procedure Call'],
      listData: [],
      updated_at: '',
      total: '',
      search_text: '',
      pagination: {
        pageSize: 10,
        size: 'small',
        onChange: (page) => {
          document.querySelector('#app').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          })
        }
      },
      readmeContent: '',
      project: '',
      spinning: true,
      shieldsShow: false,
      timer: '',
      showInfo: false,
      showLast: false,
      versionSpinning: true,
      lastData: [],
      lastProject: '',
      searchData: [],
      searchCount: 0,
      trending: false,
      trendData: []
    }
  },
  watch: {
  },
  methods: {
    trendClick () {
      this.spinning = true
      this.listData = []
      if (this.trending) {
        this.searchData = this.trendData
        this.spinning = false
        return
      }
      this._getGithubTrending()
    },
    lastClick (project, url, repo) {
      this.versionSpinning = true
      if (this.project === project && this.showLast) {
        this.showLast = false
        this.project = ''
        return
      }
      if (this.lastProject !== project && url.indexOf('release') !== -1) {
        this._getGithubRelases(repo)
      } else if (this.lastProject !== project && url.indexOf('commit') !== -1) {
        this._getGithubTags(repo, 'lastData')
      } else {
        this.versionSpinning = false
      }

      this.project = project
      this.lastProject = project
      this.showLast = true
      this.showInfo = false
      // document.querySelector('#' + project).scrollIntoView({
      //   behavior: 'smooth',
      //   block: 'center'
      // })
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
      // document.querySelector('#' + project).scrollIntoView({
      //   behavior: 'smooth',
      //   block: 'center'
      // })
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
      this.spinning = true
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
            this._getGithubLatest(search)
            if (this.listData.length === 0) {
              this._getGithubTags(search, 'listData')
            }
            if (this.listData.length === 0) {
              this._getSearchGithub(search)
            }
          } else {
            this.spinning = false
          }
        } else {
          this.spinning = false
        }
      }).catch((e) => {
        this.$message.error('获取数据失败')
        console.log(e)
      })
    },
    _getGithubTags (repo, target) {
      let graphqlUrl = 'https://api.github.com/graphql'
      let postData = {
        'query': '{repository(owner: "' + repo.split('/')[0] + '", name: "' + repo.split('/')[1] + '") {refs(refPrefix: "refs/tags/", first: 10, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {edges {node {name target {commitUrl ... on Tag {message tagger {date}} ... on Commit {committedDate}}}}}}}'
      }
      let token = '99510f2ccf40e496d1e97dbec9f31cb16770b884'
      let headers = { 'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'token ' + token }
      this.$axios.post(graphqlUrl, postData, { headers }).then((res) => {
        if (res.data['data']['repository'] !== null && res.data['data']['repository'].hasOwnProperty('refs')) {
          let lastTags = res.data['data']['repository']['refs']['edges']
          this[target] = []
          for (let item in lastTags) {
            this[target].push({
              'tag_name': lastTags[item]['node']['name'],
              'html_url': lastTags[item]['node']['target']['commitUrl'] || '',
              'created_at': lastTags[item]['node']['target'].hasOwnProperty('tagger') ? lastTags[item]['node']['target']['tagger']['date'] : lastTags[item]['node']['target']['committedDate'],
              'project': repo,
              'repo': repo,
              'body': lastTags[item]['node']['target']['message'],
              'hosting': 'github',
              'type': 'None'
            })
            if (target === 'listData') {
              this.total = this.listData.length
              this.updated_at = new Date()
              break
            }
          }
        }
        if (this[target].length === 0) {
          this.$message.error('未找到项目的tags')
        }
        this.versionSpinning = false
        this.spinning = false
      }).catch((e) => {
        this.$message.error('获取项目的tags失败')
        console.log(e)
      })
    },
    _getGithubRelases (repo) {
      let repoUrl = 'https://api.github.com/repos/' + repo + '/releases?per_page=10'
      this.$axios.get(repoUrl).then((res) => {
        this.lastData = res.data
        this.versionSpinning = false
      }).catch((e) => {
        this.$message.error('获取项目的releases失败')
        console.log(e)
      })
    },
    _getGithubLatest (repo) {
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
          'repo': repo,
          'hosting': 'github',
          'type': 'None'
        }
        this.listData = [data]
        this.total = this.listData.length
        this.updated_at = new Date()
        this.spinning = false
      }).catch((e) => {
        this.$message.error('没有找到项目的latest release版本！')
        console.log(e)
      })
    },
    _getSearchGithub (repo) {
      let searchUrl = 'https://api.github.com/search/repositories?q=' + repo + '+in:name&sort=stars&order=desc&per_page=10'
      this.$axios.get(searchUrl).then((res) => {
        this.searchData = []
        this.searchCount = res.data['total_count']
        for (let item in res.data['items']) {
          let data = {
            'full_name': res.data['items'][item]['full_name'],
            'html_url': res.data['items'][item]['html_url'],
            'description': res.data['items'][item]['description'],
            'forks_count': res.data['items'][item]['forks_count'],
            'stargazers_count': res.data['items'][item]['stargazers_count'],
            'language': res.data['items'][item]['language'],
            'updated_at': res.data['items'][item]['updated_at']
          }
          this.searchData.push(data)
        }
        this.spinning = false
      }).catch((e) => {
        this.$message.error('没有搜索到项目！')
        console.log(e)
      })
    },
    _getGithubTrending () {
      let url = 'https://github-trending-api.now.sh/repositories'
      this.$axios.get(url).then((res) => {
        this.trendData = []
        for (let item in res.data) {
          let data = {
            'full_name': res.data[item]['author'] + '/' + res.data[item]['name'],
            'html_url': res.data[item]['url'],
            'description': res.data[item]['description'],
            'forks_count': res.data[item]['forks'],
            'stargazers_count': res.data[item]['stars'],
            'language': res.data[item]['language'],
            'currentPeriodStars': res.data[item]['currentPeriodStars']
          }
          this.trendData.push(data)
        }
        this.searchData = this.trendData
        this.spinning = false
        this.trending = true
      }).catch((e) => {
        this.$message.error('获取失败！')
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

<style lang=less scoped>
@min-width: 1000px;

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
  @media screen {
    @media (min-width: @min-width) {
      width: 1140px;
    }
  }
  margin: 0 auto;
  padding: 0 10px;
  border-bottom: 1px solid #dcdfe6;
}
.title {
  color: #409eff;
  font-size: 26px;
  font-weight: 500;
  font-family: "微软雅黑";
  @media screen {
    @media (max-width: @min-width) {
      padding-left: 5px;
    }
  }
}
.title-desc {
  color: rgba(0, 0, 0, 0.45);
  margin-left: 10px;
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
}
.list-title {
  font-size: 16px;
  font-weight: bolder;
  font-family: "微软雅黑";
}
.main {
  position: relative;
  @media screen {
    @media (min-width: @min-width) {
      width: 1140px;
    }
  }
  height: -webkit-calc(100% - 80px);
  height: -moz-calc(100% - 80px);
  height: calc(100% - 80px);
  margin: 0 auto;
  padding: 10px 0;
  top: 80px;
}
.search {
  @media screen {
    @media (min-width: @min-width) {
      width: 600px;
    }
    @media (max-width: @min-width) {
      font-size: 12px;
      padding: 50px 10px 20px;
    }
  }
  margin: 0 auto;
  text-align: center;
  padding: 50px 10px;
}
.content {
  width: 100%;
  padding: 0px 80px 20px 80px;
  @media screen {
    @media (max-width: @min-width) {
      padding: 0 20px 20px 20px;
    }
  }
}
.ant-list-item-meta-description {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
  .tag-title {
    @media screen {
      @media (max-width: @min-width) {
        display: none;
      }
    }
  }
  .ant-tag {
    @media screen {
      @media (max-width: @min-width) {
        margin: 0;
      }
    }
  }
}
.tips {
  margin-top: 10px;
  font-size: 14px;
}
.tips-tag {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
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
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
}
.list-header {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
}
.info-title {
  font-size: 20px;
  @media screen {
    @media (max-width: @min-width) {
      font-size: 14px;
    }
  }
}
.repo-desc {
  width: 100%;
  word-break: break-word;
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
  /deep/ img {
    width: 100%;
  }
  /deep/ pre code {
    display: block;
    overflow: auto;
    background: #f4f4f4;
    padding: 5px 10px;
    border: 1px solid #eee;
    word-wrap: break-word;
    white-space: pre-wrap;
  }
  /deep/ code {
    overflow: auto;
    padding: 1px;
    background: #f4f4f4;
    border: 1px solid #eee;
    word-wrap: break-word;
    white-space: pre-wrap;
  }
}
</style>
