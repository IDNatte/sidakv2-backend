"""Application user admin registrator"""


from flask.cli import with_appcontext
from app.helper.db_helper import set_password
from app.model import User
import click


def teardown_admin(e=None):
    pass


def create_admin(username, password):
    user_check = User.objects().filter(lvl=1, is_active=True).count()
    if user_check == 0:

        click.echo(
            f'[*]--> Registering user "{username}" with password "{password}"')
        user = User(username=username, email='admin@admin.com',
                    password=set_password(password), lvl=1, is_active=True)
        user.save()

        click.echo('[*]--> User admin registered\n')
        click.echo(f'[*]--> Username : {user.username}')
        click.echo(f'[*]--> Password : {password}')
        click.echo(f'[*]--> email : {user.email}')
        click.secho(
            '\n[!]--> Please copy paste info above somhere else and keep it save !\n', fg="red", bold=True)

    else:
        click.echo('[!] Admin user already created, operation exit...')
        raise click.Abort()


@click.command('admin', help="Create admin user if no registered admin user in database")
@click.option('--user', default='admin', help="Username value", required=True)
@click.option('--pwd', default='password', help="Password value", required=True)
@with_appcontext
def init_create_admin(user, pwd):
    create_admin(user, pwd)


def init_admin(app):
    app.teardown_appcontext(teardown_admin)
    app.cli.add_command(init_create_admin)
