def prac_2():
  codes='''from pyspark.sql import SparkSession
  # Initialize SparkSession
  spark = SparkSession.builder.appName("RDD").getOrCreate()
  # Create an RDD from a list
  data = [1, 2, 3, 4, 5]
  rdd = spark.sparkContext.parallelize(data)
  # Transformations and Actions
  rdd_doubled = rdd.map(lambda x: x * 2)  # Double each element
  rdd_filtered = rdd.filter(lambda x: x % 2 == 0)  # Keep even numbers
  total_sum = rdd.reduce(lambda x, y: x + y)  # Sum all elements
  # Print results
  print("Original RDD:", rdd.collect())
  print("Doubled RDD:", rdd_doubled.collect())
  print("Filtered RDD (even numbers):", rdd_filtered.collect())
  print("Sum of all elements:", total_sum)
  # Stop SparkSession
  spark.stop()'''
  print(codes)

def prac_3():
  codes='''# To find min Temp
  from pyspark import SparkConf, SparkContext


  conf = SparkConf().setMaster("local").setAppName("MinTemperature")
  sc = SparkContext(conf=conf)  # Use the conf keyword argument

  # Rest of your code remains the same
  def parseLine(line):
      fields = line.split(',')
      return (
          fields[0],
          fields[2],
          float(fields[3]) * 0.1 * (9.0 / 5.0) + 32.0
      )

  lines = sc.textFile("prac3.csv")

  minTemps = (
      lines.map(parseLine)
      .filter(lambda x: x[1] == "TMIN")
      .map(lambda x: (x[0], x[2]))
      .reduceByKey(min)
      .collect()
  )

  for station, temp in minTemps:
      print(f"{station}\t{temp:.2f}F")

  sc.stop()'''
  print(codes)


def prac_4():
  #Using FlatMap function
  from pyspark import SparkContext, SparkConf

  conf = SparkConf().setMaster("local").setAppName("MinTemperature")
  sc = SparkContext(conf=conf)

  input = sc.textFile("prac4.txt")
  wordCounts = input.flatMap(lambda x : x.split()).countByValue()

  for word, count in wordCounts.items():
    print(f"{word} {count}")
  sc.stop()


def prac_5():
  codes='''#Executing SQL commands and SQL-style functions on a Data Frame
  from pyspark.sql import SparkSession

  # Create a SparkSession
  spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

  # Load and process the data
  lines = spark.read.csv("prac5.csv", inferSchema=True, header=False)
  people = lines.toDF("ID", "name", "age", "numFriends")

  # Query the data using SQL
  people.createOrReplaceTempView("people")
  teenagers = spark.sql("SELECT * FROM people WHERE age BETWEEN 13 AND 19")

  # Display the results
  teenagers.show()

  # Group and count by age
  people.groupBy("age").count().orderBy("age").show()

  # Stop the SparkSession
  spark.stop()'''
  print(codes)

def prac_6( ):
   codes='''from pyspark import SparkConf, SparkContext
  conf = SparkConf().setMaster("local").setAppName("SpendByCustomer")
  # Configure and initialize Spark
  sc = SparkContext(conf = conf)

  # Load and process the data
  results = (
      sc.textFile("prac6.csv")
      .map(lambda line: (int(line.split(',')[0]), float(line.split(',')[2])))
      .reduceByKey(lambda x, y: x + y)
      .collect()
  )

  # Display the results
  for result in results:
      print(result)

  sc.stop()'''
   print(codes)

# def prac_7():
#   from pyspark.sql import SparkSession

#   # Function to load movie names
#   def loadMovieNames():
#       with open("u.item", encoding="ISO-8859-1") as f:
#           return {int(line.split('|')[0]): line.split('|')[1] for line in f}

#   # Initialize SparkSession
#   spark = SparkSession.builder.appName("PopularMovies").getOrCreate()

#   # Load movie names and raw data
#   nameDict = loadMovieNames()
#   lines = spark.read.text("u.data").rdd.map(lambda x: int(x.value.split()[1]))

#   # Create DataFrame and calculate movie popularity
#   movieDataset = spark.createDataFrame(lines, "int").toDF("movieID")
#   topMovies = movieDataset.groupBy("movieID").count().orderBy("count", ascending=False).cache()

#   # Show top 10 movies
#   topMovies.show(10)
#   for row in topMovies.take(10):
#       print(f"{nameDict[row['movieID']]}: {row['count']}")

#   # Stop SparkSession
#   spark.stop()


# def prac_9():
#   #Using Spark ML to Produce Movie Recommendations
#   from pyspark.sql import SparkSession
#   from pyspark.ml.recommendation import ALS
#   from pyspark.ml.evaluation import RegressionEvaluator

#   # Initialize SparkSession
#   spark = SparkSession.builder.appName('recommendation').getOrCreate()

#   # Load data
#   data = spark.read.csv('rating.csv', inferSchema=True, header=True)

#   # Split data into training and testing sets
#   train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

#   # Train ALS model
#   als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating")
#   model = als.fit(train_data)

#   # Make predictions
#   predictions = model.transform(test_data)

#   # Evaluate model
#   evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
#   rmse = evaluator.evaluate(predictions)
#   print(f"Root-mean-square error = {rmse}")

#   # Get recommendations for a specific user (userId = 12)
#   single_user = test_data.filter(test_data['userId'] == 12).select(['movieId', 'userId'])
#   recommendations = model.transform(single_user).orderBy('prediction', ascending=False)
#   recommendations.show()



# def prac_10():
#   ## Streaming
#   from pyspark import SparkContext
#   from pyspark.streaming import StreamingContext
#   from pyspark.rdd import RDD

#   # Initialize SparkContext and StreamingContext
#   sc = SparkContext("local[2]", "NetworkWordCount")
#   ssc = StreamingContext(sc, 1)  # Batch interval of 1 second

#   # Simulate streaming data using a queue of RDDs
#   rdd_queue = [
#       sc.parallelize(["hello world", "hello spark"]),
#       sc.parallelize(["pyspark streaming example"]),
#       sc.parallelize(["streaming data is fun"])
#   ]

#   # Create a DStream from the RDD queue
#   lines = ssc.queueStream(rdd_queue)

#   # Process the data
#   wordCounts = (
#       lines.flatMap(lambda line: line.split(" "))
#       .map(lambda word: (word, 1))
#       .reduceByKey(lambda x, y: x + y)
#   )

#   # Output the word counts
#   wordCounts.pprint()

#   # Start the streaming context
#   ssc.start()
#   ssc.awaitTerminationOrTimeout(5)  # Run for 5 seconds
#   ssc.stop(stopSparkContext=True, stopGraceFully=True)

def prac_7():
  codes='''
  from pyspark.sql import SparkSession

  # Function to load movie names
  def loadMovieNames():
      with open("u.item", encoding="ISO-8859-1") as f:
          return {int(line.split('|')[0]): line.split('|')[1] for line in f}

  # Initialize SparkSession
  spark = SparkSession.builder.appName("PopularMovies").getOrCreate()

  # Load movie names and raw data
  nameDict = loadMovieNames()
  lines = spark.read.text("u.data").rdd.map(lambda x: int(x.value.split()[1]))

  # Create DataFrame and calculate movie popularity
  movieDataset = spark.createDataFrame(lines, "int").toDF("movieID")
  topMovies = movieDataset.groupBy("movieID").count().orderBy("count", ascending=False).cache()

  # Show top 10 movies
  topMovies.show(10)
  for row in topMovies.take(10):
      print(f"{nameDict[row['movieID']]}: {row['count']}")

  # Stop SparkSession
  spark.stop()'''
  print(codes)


def prac_9():
  codes='''
  #Using Spark ML to Produce Movie Recommendations
  from pyspark.sql import SparkSession
  from pyspark.ml.recommendation import ALS
  from pyspark.ml.evaluation import RegressionEvaluator

  # Initialize SparkSession
  spark = SparkSession.builder.appName('recommendation').getOrCreate()

  # Load data
  data = spark.read.csv('rating.csv', inferSchema=True, header=True)

  # Split data into training and testing sets
  train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

  # Train ALS model
  als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating")
  model = als.fit(train_data)

  # Make predictions
  predictions = model.transform(test_data)

  # Evaluate model
  evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
  rmse = evaluator.evaluate(predictions)
  print(f"Root-mean-square error = {rmse}")

  # Get recommendations for a specific user (userId = 12)
  single_user = test_data.filter(test_data['userId'] == 12).select(['movieId', 'userId'])
  recommendations = model.transform(single_user).orderBy('prediction', ascending=False)
  recommendations.show()
  '''
  print(codes)


def prac_10():
  codes ='''
  ## Streaming
  from pyspark import SparkContext
  from pyspark.streaming import StreamingContext
  from pyspark.rdd import RDD

  # Initialize SparkContext and StreamingContext
  sc = SparkContext("local[2]", "NetworkWordCount")
  ssc = StreamingContext(sc, 1)  # Batch interval of 1 second

  # Simulate streaming data using a queue of RDDs
  rdd_queue = [
      sc.parallelize(["hello world", "hello spark"]),
      sc.parallelize(["pyspark streaming example"]),
      sc.parallelize(["streaming data is fun"])
  ]

  # Create a DStream from the RDD queue
  lines = ssc.queueStream(rdd_queue)

  # Process the data
  wordCounts = (
      lines.flatMap(lambda line: line.split(" "))
      .map(lambda word: (word, 1))
      .reduceByKey(lambda x, y: x + y)
  )

  # Output the word counts
  wordCounts.pprint()

  # Start the streaming context
  ssc.start()
  ssc.awaitTerminationOrTimeout(5)  # Run for 5 seconds
  ssc.stop(stopSparkContext=True, stopGraceFully=True)
  '''
  print(codes)


