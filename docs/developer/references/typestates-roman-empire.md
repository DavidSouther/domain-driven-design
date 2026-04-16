Typestates Would Have Saved the Roman Republic
            
                                
Disclaimer: this post may contain some historical inaccuraciesAn approximation of what Rome may have looked like circa 50 BCThe year is 50 BC and we're in a sunny, happy and peaceful Roman republic. People are frequenting the baths, theaters, and temples, and the average plebeian doesn't have a care in the world.Suddenly, a small land dispute over the entire Mediterranean forces an unexpecting Rome into war. The way this normally worked in Rome is that a single person called a dictator would be nominated in place of the democratically elected consuls, and when the war ended the consuls would be reinstated. We know from historical records that Romans used JavaScript rather than TypeScript, but for the sake of illustration, we can use this type definition to describe the above process:

```
enum Ruler {
  Consuls = \"consuls\",
  Dictator = \"dictator\",
}

enum Status {
  Peace = \"peace\",
  War = \"war\",
}

interface Rome {
  ruler: Ruler;
  status: Status;
}
```

The Roman state machine had two actions: `GO_TO_WAR`, which changed the status to `Status.War` and the ruler to `Ruler.Dictator` and `MAKE_PEACE` - which changed the status to `Status.Peace` and the ruler to `Ruler.Consuls`.

The Romans fought hard and long, and eventually the time came to put down their swords and go build some aqueducts. MAKE_PEACE was sent and everyone rejoiced. The dictator gave control to the consuls, and all was well.Or that is what would have happened, except that the dictator nominated for this war was one Julius Caesar. Julius had just made some changes to MAKE_PEACE in his last PR and introduced a bug which causes the ruler property not to be changed to Ruler.Consuls. This was missed in code review and so made it into the Roman production. Due to the above bug, after dispatching MAKE_PEACE, Rome found themselves in an invalid state where the republic is at peace, but the ruler is a dictator. This did not fit the business requirement, but it was already too late. Unwilling to expand the scope of the current sprint, the Romans branded themselves as an empire, marked the resulting ticket as \"wontfix\", and continued onward. What could have they done to prevent this?Essentially the Romans expressed the following state machine:They also had a singular definition of what the type of their context was, which prevented their CI from catching the bug Julius introduced. As far as TypeScript is concerned, the Roman context ruler can be any Ruler enum member at any time.If they would have changed the type definition as follows:

```
enum Ruler {
  Consuls = \"consuls\",
  Dictator = \"dictator\",
}

enum Status {
  Peace = \"peace\",
  War = \"war\",
}

interface RomeAtWar {
  ruler: Ruler.Dictator,
  status: Status.War
}

interface RomeAtPeace {
  ruler: Ruler.Consuls;
  status: Status.Peace;
}

type Rome = RomeAtPeace | RomeAtWar;
```

Using a discriminated union with status as the discriminating property (status also being the state machine value in this case), a state with a Ruler.Dictator ruler and a status of Status.Peace would have been invalid, and the bug would never have made the CI.This applies the concept of typestates - Defining the type of our context according to the current state value. By doing this we codify our business logic into the type system and essentially make an invalid state unrepresentable.In the same way that state machines add an additional \"dimension\" over \"flat\" state which does not control transitions or prevent you from sending an action at the wrong time, typestates force you to populate the context in accordance with the current state value. If only the Romans knew...
                
Yoav Lavi's Blog