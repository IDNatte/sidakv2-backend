"""Database Collection populator"""


from app.model import Organization, SectoralGroup, User
from flask.cli import with_appcontext
import click


def teardown_populate(e=None):
    pass


def run_populate():
    user_check = User.objects().count()
    org_check = Organization.objects().count()
    sectoral_check = SectoralGroup.objects().count()

    if org_check == 0 and sectoral_check == 0:
        click.echo(
            '[!] No data created, running data population synchronously...\n')

        click.echo('[*]--> Populating sectoral group table...')
        sectoral = [
            SectoralGroup(sector_name='sektor sosial'),
            SectoralGroup(sector_name='sektor ekonomi'),
            SectoralGroup(sector_name='sektor lingkungan')
        ]

        SectoralGroup.objects.insert(sectoral)

        click.echo('[*]--> Populating organization table...')
        soc_sector = SectoralGroup.objects.filter(
            sector_name='sektor sosial').get()
        env_sector = SectoralGroup.objects.filter(
            sector_name='sektor lingkungan').get()
        eco_sector = SectoralGroup.objects.filter(
            sector_name='sektor ekonomi').get()

        eco_org = [
            Organization(org_name="Dinas Perdagangan",
                         sector_group=soc_sector),
            Organization(org_name="Dinas Perindustrian",
                         sector_group=soc_sector),
            Organization(org_name="Bappelitbang", sector_group=soc_sector),
            Organization(org_name="DPMPTSP", sector_group=soc_sector),
            Organization(org_name="BPKAD", sector_group=soc_sector),
            Organization(org_name="BPPRD", sector_group=soc_sector),
        ]

        env_org = [
            Organization(org_name="Dinas Perhubungan",
                         sector_group=env_sector),
            Organization(org_name="Dinas Lingkungan Hidup",
                         sector_group=env_sector),
            Organization(org_name="Dinas Ketahanan Pangan",
                         sector_group=env_sector),
            Organization(org_name="Dinas Perikanan", sector_group=env_sector),
            Organization(org_name="Donas Pertanian", sector_group=env_sector),
            Organization(org_name="Dinas Perikanan", sector_group=env_sector),
            Organization(org_name="DISPUTARSIP", sector_group=env_sector),
            Organization(org_name="BPBD", sector_group=env_sector),

        ]

        social_org = [
            Organization(org_name="Dinas sosial", sector_group=eco_sector),
            Organization(org_name="Dinas Kesehatan", sector_group=eco_sector),
            Organization(org_name="RSU Datu Sanggul", sector_group=eco_sector),
            Organization(org_name="Dinas Pendidikan", sector_group=eco_sector),
            Organization(org_name="DISNAKER", sector_group=eco_sector),
            Organization(org_name="DISPORA", sector_group=eco_sector),
            Organization(org_name="DISBUDPAR", sector_group=eco_sector),
            Organization(org_name="Dinas Kominfo", sector_group=eco_sector),
            Organization(org_name="Dinas Kominfo", sector_group=eco_sector),
            Organization(org_name="DISDUKCAPIL", sector_group=eco_sector),
            Organization(org_name="BKPSDM", sector_group=eco_sector),
            Organization(org_name="DPPKB", sector_group=eco_sector),
            Organization(org_name="DPMD", sector_group=eco_sector),
            Organization(org_name="DPMD", sector_group=eco_sector),
        ]

        Organization.objects.insert(eco_org)
        Organization.objects.insert(env_org)
        Organization.objects.insert(social_org)

    else:
        click.echo('[!] Data already populated, operation exit...')
        raise click.Abort()


@click.command('populate', help="Pre-populate data in database collection except user collection")
@with_appcontext
def init_populate_db():
    run_populate()


def init_populator(app):
    app.teardown_appcontext(teardown_populate)
    app.cli.add_command(init_populate_db)
