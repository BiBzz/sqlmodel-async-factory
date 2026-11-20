from factories import HeroFactory

hero = HeroFactory.build()
print(hero.id, hero.name, hero.team.name)

heroes = HeroFactory.build_batch(2, age=48)
print([(hero.name, hero.age) for hero in heroes])
