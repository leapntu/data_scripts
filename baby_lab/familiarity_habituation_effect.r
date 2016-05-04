library(plyr)
df <- read.csv("df.csv")
diff <- ddply(df,'id', function(x) {
  words = x[x$type == 'word',]$looking
  parts = x[x$type == 'part',]$looking
  data.frame(t = t.test(words, parts)$statistic)
})

hist(diff$t)
