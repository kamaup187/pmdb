# import os
# from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand

# from app import  db,create_app

# configuration = os.getenv('APP_SETTINGS')
# # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>','running',configuration,'migrations<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

# app = create_app(configuration)
# # app.config.from_object(os.environ['APP_SETTINGS'])

# migrate = Migrate(app, db)
# manager = Manager(app)

# manager.add_command('db', MigrateCommand)


# if __name__ == '__main__':
#     manager.run()