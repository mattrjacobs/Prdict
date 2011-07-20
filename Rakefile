# Rakefile for Prdict-API
# Interesting targets are:
#  $ clean            : removes non-source artifacts
#  $ test             : runs unit tests
#  $ package          : assembles the whole webapp in a form suitable for
#                       deployment or running with dev_appserver.py
#  $ run              : runs the existing webapp with dev_appserver.py
#  $ run_clean        : runs the webpp with a clear datastore
#  $ run_sqlite       : runs the webapp with a SQLite datastore in $TMPDIR
#  $ backup_sqlite    : saves the current SQLite datastore to a new path in $TMPDIR
#  $ clear_sqlite     : deletes the SQLite datastore
#  $ restore_sqlite   : restores the SQLite datastore from its backup
#  $ git_check_local  : checks if all local files are checked in
#  $ git_check_remote : checks if local repo is up-to-date
#  $ update_version   : updates Prdict-API version (in src and target) with 
#    		        user-specified version number and checks in version in src
#  $ deploy           : pushes code to production
#  $ release          : releases code to production, tests it there and 
#                       notifies devs when ready for GAE version switch
#  $ push             : does a git push and a release
#  $ itest:run        : runs all of the integration tests against localhost:8080
#  $ devserver:start  : starts the dev server at localhost:8080
#  $ devserver:stop   : stops the dev server

desc "determine if git status returns no local diffs from repo"
task :git_check_local do
  sh "bin/git_check_local.sh"
end

desc "determine if git pull returns no remote diffs from repo"
task :git_check_remote do
  sh "bin/git_check_remote.sh"
end

desc "execute a push to the remote repo and a release of the code in one shot"
task :push, :release_size, :needs => [:test, :git_check_remote, :clean, "itest:run", :init_deploy_password, "target/itest"] do |t, args|
  sh "git push"
  if args[:release_size].nil?
     release_size = 'Minor'
  else
     release_size = args[:release_size]
  end
  Rake::Task[ "update_version" ].execute(:release_size => args[:release_size])
  Rake::Task[ "package" ].execute
  Rake::Task[ "deploy" ].execute
  #Rake::Task[ "itest:release" ].execute
  print "DEPLOYMENT WORKED!\n"
end

desc "updates version info in app.yaml and checks that in"
task :update_version, :release_size, :needs => ["package", "git_check_local", "git_check_remote"] do |t, args|
  if args[:release_size].nil?
     release_size = 'Minor'
  else
     release_size = args[:release_size]
  end
  if release_size != 'Major' && release_size != 'CrazyGoNuts'
     release_size = 'Minor'
  end
  old_release_number = File.read("target/release_number.txt").chomp()
  pieces = old_release_number.split('-')
  case release_size
      when 'Minor'
          new_release_number = pieces[0] + "-" + pieces[1] + "-" + (pieces[2].to_i + 1).to_s
      when 'Major'
          new_release_number = pieces[0] + "-" + (pieces[1].to_i + 1).to_s + "-0"
      when 'CrazyGoNuts'
          new_release_number = (pieces[0].to_i + 1).to_s + "-0-0"
  end
  sed_command = "sed -i '' 's/^version: [0-9|-]*/version: " + new_release_number + "/' "
  sh sed_command + "target/webapp/app.yaml" 
  sh sed_command + "src/main/webapp/app.yaml" 
  release_message = "'Prdict API release from " + old_release_number + " to " + new_release_number + "'"
  git_commit_cmd = "git commit src/main/webapp/app.yaml -m " + release_message
  sh git_commit_cmd
  sh "git push"
end

task :init_deploy_password => ["target"] do
  File.open("target/deploy_password.txt", 'w') do |file|
    file.write("ibb5SeyXecL4")
  end    				      				  
end

desc "deploys webapp to production"
task :deploy => [:package, :init_deploy_password] do
  sh "appcfg.py update target/webapp --email=prdictapi.deployer@gmail.com --passin < target/deploy_password.txt"
end

desc "sample release task that checkpoints codebase and commits it, then deploys current codebase to GAE and confirms it works as expected"
task :release, :release_size, :needs => [:test, :git_check_local, :git_check_remote, :clean, "itest:run", :init_deploy_password, "target/itest"] do |t, args|
  if args[:release_size].nil?
     release_size = 'Minor'
  else
     release_size = args[:release_size]
  end
  Rake::Task[ "update_version" ].execute(:release_size => args[:release_size])
  Rake::Task[ "package" ].execute
  Rake::Task[ "deploy" ].execute
  #Rake::Task[ "itest:release" ].execute
  print "DEPLOYMENT WORKED!\n"
end

desc "remove generated artifacts"
task :clean do
  sh "rm -fr target"
  sh "find . -name \"*~\" | xargs rm -f"
  sh "find . -name \"*.pyc\" | xargs rm -f"
end

directory "target"
directory "target/itest"
directory "target/webapp"
directory "target/webapp/templates"

# initialize all properties which get set at build time (release/build #s)
task :initialize => ["target", "target/webapp"] do
  sh "bin/getbuild.sh target/build.txt"
  sh "awk '{print \"s/%BUILD%/\" $1 \"/\"}' target/build.txt > target/build.sed"
  sh "egrep '^version' src/main/webapp/app.yaml | awk '{ print $2 }' > target/release_number.txt"
  sh "awk '{print \"s/%RELEASE_NUMBER%/\" $1 \"/\"}' target/release_number.txt > target/release_number.sed"
  sh "sed -f target/build.sed src/main/webapp/app.yaml > target/webapp/app.yaml"
end

task :static_dir => [:initialize] do
  sh "mkdir -p target/webapp/static-`cat target/build.txt`"
  sh "bin/instantiate_css src/main/webapp/static/scss target/webapp/static-`cat target/build.txt`/css"
end

desc "generate resources for inclusion in the package"
task :package => [:static_dir] do
  sh "cp src/main/webapp/cron.yaml target/webapp/cron.yaml"
  sh "cp src/main/webapp/index.yaml target/webapp/index.yaml"
  sh "cp -r src/main/webapp/static/* target/webapp/static-`cat target/build.txt`"
  sh "bin/rpackage src/main/python target/webapp"
  sh "bin/rpackage src/main/webapp/templates target/webapp/templates"
  sh "sed -f target/build.sed -i '' target/webapp/build.py"
  sh "sed -f target/release_number.sed -i '' target/webapp/release_number.py"
end

desc "run unit tests; can specify an optional argument to only run one test"
task :test, :test_file do |t, args|
  if args[:test_file].nil?
    sh "bin/run_test src/test"
  else
    sh "bin/run_test src/test " + args[:test_file]
  end
end

namespace :devserver do
  desc "starts dev server"
  task :start => [:package] do
    sh "bin/start_devserver target/webapp target/appserver.pid"
  end

  desc "stops dev server"
  task :stop do
    sh "bin/stop_devserver target/appserver.pid"
  end
end

namespace :itest do
  desc "perform integration tests"
  task :run => [:package] do
    Rake::Task[ "devserver:stop" ].execute 
    Rake::Task[ "devserver:start" ].execute
    sh "bin/run_itest src/itest target/itest_results.txt"
    Rake::Task[ "devserver:stop" ].execute 
    sh "bin/summarize_test_results target/itest_results.txt"
  end

  #desc "runs ITests against recently deployed prod candidate"
  #task :release => ["package", "target/release_number.txt", "target/itest"] do
  #  release_number = File.read("target/release_number.txt").chomp() + ".latest.prdictapi.appspot.com"
  #  print "Going to run ITests against " + release_number + "\n"
  #  sh "bin/rpackage src/itest/python target/itest"
  #  sed_cmd = "sed -i '' 's/localhost:8080/" + release_number + "/' target/itest/itest.py"
  #  sh sed_cmd
  #  sh "bin/run_itest target/itest target/itest_results.txt"
  #  sh "bin/summarize_test_results target/itest_results.txt"
  # end
end

desc "run the app in a dev server"
task :run => [:package] do
  sh "bin/run"
end

desc "run the app in a dev server with a cleared datastore"
task :run_clean => [:package] do
  sh "bin/run_clean_datastore"
end

desc "run the app in a dev server with a SQLite datastore"
task :run_sqlite => [:package] do
  sh "bin/run_sqlite_datastore"
end

desc "saves the SQLite DB to a new path in $TMPDIR"
task :backup_sqlite do
  sh "cp $TMPDIR/dev_appserver.datastore $TMPDIR/dev_appserver.datastore.backup"
end

desc "clears the SQLite DB"
task :clear_sqlite do
  sh "rm $TMPDIR/dev_appserver.datastore"
end

desc "restores the SQLite DB from its backup"
task :restore_sqlite do
  sh "cp $TMPDIR/dev_appserver.datastore.backup $TMPDIR/dev_appserver.datastore"
end

# for convenience when programming
desc "Default task = package"
task :default => [:package]
