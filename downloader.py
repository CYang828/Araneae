#*-*coding:utf8*-*

import Araneae.file as FILE

class BaseDownloader(object):

    def push(self,file_obj):
        raise NotImplementedError('下载器需要实现push方法')

    def download(self,file_obj):
        """
        下载文件
        """
        req = REQ.Request(downloadItem.url, 1,
                          method = downloadItem.method,
                          cookies = downloadItem.cookie,
                          timeout = 30,
                          headers = {'User-Agent': userAgent})

        response = req.fetch()
        # print 'Response Header[%s]' % response.headers

        ContentType = response.headers['Content-Type']

        if 'application/octet-stream' == ContentType:

            headerContext = response.headers['Content-Disposition']
            match = re.search(r'[.]*?filename=(.*)', headerContext)

            if match is None:
                print "Content-Disposition [%s] ERROR!" % headerContext
                return -1
            else:
                fileName = match.group(1)
                print 'Download FileName[%s]' % fileName

                fileName = downloadItem.fpath
                with open(fileName, "wb") as code:
                    code.write(response.content)
        else:
            print "Content-Type[%s] Error!" % ContentType

