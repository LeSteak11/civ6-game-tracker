-- Version 1
CREATE TABLE "Alliances" (
		"AllianceType" TEXT,
		"Name" TEXT NOT NULL DEFAULT """",
		"Description" TEXT NOT NULL DEFAULT """",
		PRIMARY KEY(AllianceType),
		FOREIGN KEY (AllianceType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AllianceEffects" (
		"LevelRequirement" INTEGER NOT NULL DEFAULT 0,
		"AllianceType" TEXT,
		"ModifierID" TEXT,
		PRIMARY KEY(LevelRequirement, AllianceType, ModifierID),
		FOREIGN KEY (ModifierID) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AllianceType) REFERENCES Alliances(AllianceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CommemorationModifiers" (
		"CommemorationType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(CommemorationType, ModifierId),
		FOREIGN KEY (CommemorationType) REFERENCES CommemorationTypes(CommemorationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CommemorationTypes" (
		"CommemorationType" TEXT NOT NULL,
		"CategoryDescription" LocalizedText,
		"GoldenAgeBonusDescription" LocalizedText,
		"NormalAgeBonusDescription" LocalizedText,
		"DarkAgeBonusDescription" LocalizedText,
		"MinimumGameEra" TEXT,
		"MaximumGameEra" TEXT,
		PRIMARY KEY(CommemorationType),
		FOREIGN KEY (MinimumGameEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MaximumGameEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ComplimentModifiers" (
		"CommemorationType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(CommemorationType, ModifierId),
		FOREIGN KEY (CommemorationType) REFERENCES CommemorationTypes(CommemorationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticActions_XP1" (
		"DiplomaticActionType" TEXT NOT NULL,
		"RequiresGoldenAgeCommemorationType" TEXT,
		"AllianceType" TEXT,
		"RequiresBrokenPromise" BOOLEAN NOT NULL CHECK (RequiresBrokenPromise IN (0,1)) DEFAULT 0,
		"RequiresDifferentLateGovernment" BOOLEAN NOT NULL CHECK (RequiresDifferentLateGovernment IN (0,1)) DEFAULT 0,
		"RequiresAllianceSoonToEnd" BOOLEAN NOT NULL CHECK (RequiresAllianceSoonToEnd IN (0,1)) DEFAULT 0,
		PRIMARY KEY(DiplomaticActionType),
		FOREIGN KEY (DiplomaticActionType) REFERENCES DiplomaticActions(DiplomaticActionType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (RequiresGoldenAgeCommemorationType) REFERENCES CommemorationTypes(CommemorationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AllianceType) REFERENCES Alliances(AllianceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticVisibilitySources_XP1" (
		"VisibilitySourceType" TEXT NOT NULL,
		"TradePostTrait" TEXT,
		PRIMARY KEY(VisibilitySourceType),
		FOREIGN KEY (VisibilitySourceType) REFERENCES DiplomaticVisibilitySources(VisibilitySourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TradePostTrait) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "EmergencyAlliances" (
		"EmergencyType" TEXT NOT NULL,
		"Trigger" TEXT NOT NULL,
		"TargetRequirementSet" TEXT,
		"GoalTrigger" TEXT NOT NULL,
		"MemberRequirementSet" TEXT,
		"Duration" INTEGER NOT NULL DEFAULT 0,
		"RemovesWarState" BOOLEAN NOT NULL CHECK (RemovesWarState IN (0,1)) DEFAULT 1,
		"ShareVis" BOOLEAN NOT NULL CHECK (ShareVis IN (0,1)) DEFAULT 0,
		"OpenBorders" BOOLEAN NOT NULL CHECK (OpenBorders IN (0,1)) DEFAULT 0,
		"KillFriendship" BOOLEAN NOT NULL CHECK (KillFriendship IN (0,1)) DEFAULT 1,
		"WarOnTarget" BOOLEAN NOT NULL CHECK (WarOnTarget IN (0,1)) DEFAULT 1,
		"InformTarget" BOOLEAN NOT NULL CHECK (InformTarget IN (0,1)) DEFAULT 1,
		"LockoutTime" INTEGER NOT NULL DEFAULT 0,
		"EmergencyText" TEXT NOT NULL,
		"GoalText" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		PRIMARY KEY(EmergencyType),
		FOREIGN KEY (MemberRequirementSet) REFERENCES RequirementSets(RequirementSetId) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (EmergencyType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (EmergencyText) REFERENCES EmergencyTexts(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GoalText) REFERENCES EmergencyGoalTexts(GoalType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "EmergencyBuffs" (
		"ModifierID" TEXT NOT NULL,
		"EmergencyType" TEXT NOT NULL,
		"Description" TEXT,
		PRIMARY KEY(ModifierID, EmergencyType),
		FOREIGN KEY (EmergencyType) REFERENCES EmergencyAlliances(EmergencyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ModifierID) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "EmergencyGoalTexts" (
		"GoalType" TEXT NOT NULL UNIQUE,
		"GoalDescription" TEXT,
		"ShortGoalDescription" TEXT,
		"TentativeGoalDescription" TEXT,
		"ShortTargetGoalDescription" TEXT,
		"ListGoal" TEXT,
		"TargetListGoal" TEXT,
		PRIMARY KEY(GoalType));

CREATE TABLE "EmergencyRewards" (
		"ModifierID" TEXT NOT NULL,
		"EmergencyType" TEXT NOT NULL,
		"OnSuccess" BOOLEAN NOT NULL CHECK (OnSuccess IN (0,1)),
		"Description" TEXT,
		"FirstPlace" BOOLEAN NOT NULL CHECK (FirstPlace IN (0,1)) DEFAULT 0,
		"TopTier" BOOLEAN NOT NULL CHECK (TopTier IN (0,1)) DEFAULT 0,
		"BottomTier" BOOLEAN NOT NULL CHECK (BottomTier IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ModifierID, EmergencyType, OnSuccess),
		FOREIGN KEY (EmergencyType) REFERENCES EmergencyAlliances(EmergencyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ModifierID) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "EmergencyTexts" (
		"Type" TEXT NOT NULL UNIQUE,
		"Flavor" TEXT,
		"Description" TEXT,
		"ExtraEffects" TEXT,
		"ExtraRewards" TEXT,
		"ExtraFailureRewards" TEXT,
		"DescriptionShorter" TEXT,
		PRIMARY KEY(Type));

CREATE TABLE "Eras_XP1" (
		"EraType" TEXT NOT NULL,
		"GameEraMinimumTurns" INTEGER,
		"GameEraMaximumTurns" INTEGER,
		"LiberatedEnvoys" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(EraType),
		FOREIGN KEY (EraType) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Governors" (
		"GovernorType" TEXT NOT NULL,
		"Name" LocalizedText NOT NULL,
		"Description" LocalizedText NOT NULL,
		"IdentityPressure" INTEGER NOT NULL DEFAULT 0,
		"Title" LocalizedText NOT NULL,
		"ShortTitle" LocalizedText NOT NULL,
		"TransitionStrength" INTEGER NOT NULL DEFAULT 0,
		"AssignCityState" BOOLEAN NOT NULL CHECK (AssignCityState IN (0,1)) DEFAULT 0,
		"Image" TEXT NOT NULL DEFAULT "NO_IMAGE",
		"PortraitImage" TEXT NOT NULL,
		"PortraitImageSelected" TEXT NOT NULL,
		"TraitType" TEXT,
		PRIMARY KEY(GovernorType),
		FOREIGN KEY (GovernorType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernorsCannotAssign" (
		"GovernorType" TEXT NOT NULL,
		"CannotAssign" BOOLEAN NOT NULL CHECK (CannotAssign IN (0,1)),
		PRIMARY KEY(GovernorType),
		FOREIGN KEY (GovernorType) REFERENCES Governors(GovernorType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernorModifiers" (
		"GovernorType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(GovernorType, ModifierId),
		FOREIGN KEY (GovernorType) REFERENCES Governors(GovernorType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernorPromotions" (
		"GovernorPromotionType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"Level" INTEGER NOT NULL DEFAULT 0,
		"Column" INTEGER NOT NULL DEFAULT 0,
		"BaseAbility" BOOLEAN NOT NULL CHECK (BaseAbility IN (0,1)) DEFAULT 0,
		PRIMARY KEY(GovernorPromotionType));

CREATE TABLE "GovernorPromotionConditions" (
		"GovernorPromotionType" TEXT NOT NULL,
		"HiddenWithoutPrereqs" BOOLEAN NOT NULL CHECK (HiddenWithoutPrereqs IN (0,1)),
		"EarliestGameEra" TEXT,
		PRIMARY KEY(GovernorPromotionType),
		FOREIGN KEY (EarliestGameEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GovernorPromotionType) REFERENCES GovernorPromotions(GovernorPromotionType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernorPromotionModifiers" (
		"GovernorPromotionType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(GovernorPromotionType, ModifierId),
		FOREIGN KEY (GovernorPromotionType) REFERENCES GovernorPromotions(GovernorPromotionType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernorPromotionPrereqs" (
		"GovernorPromotionType" TEXT NOT NULL,
		"PrereqGovernorPromotion" TEXT NOT NULL,
		PRIMARY KEY(GovernorPromotionType, PrereqGovernorPromotion),
		FOREIGN KEY (GovernorPromotionType) REFERENCES GovernorPromotions(GovernorPromotionType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqGovernorPromotion) REFERENCES GovernorPromotions(GovernorPromotionType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernorPromotionSets" (
		"GovernorType" TEXT NOT NULL,
		"GovernorPromotion" TEXT NOT NULL,
		PRIMARY KEY(GovernorType, GovernorPromotion),
		FOREIGN KEY (GovernorType) REFERENCES Governors(GovernorType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GovernorPromotion) REFERENCES GovernorPromotions(GovernorPromotionType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernorReplaces" (
		"UniqueGovernorType" TEXT NOT NULL,
		"ReplacesGovernorType" TEXT NOT NULL,
		PRIMARY KEY(UniqueGovernorType, ReplacesGovernorType),
		FOREIGN KEY (UniqueGovernorType) REFERENCES Governors(GovernorType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ReplacesGovernorType) REFERENCES Governors(GovernorType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatWorks_MODE" (
		"GreatWorkType" TEXT NOT NULL,
		"RequiredGovernor" TEXT,
		PRIMARY KEY(GreatWorkType),
		FOREIGN KEY (GreatWorkType) REFERENCES GreatWorks(GreatWorkType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (RequiredGovernor) REFERENCES Governors(GovernorType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Happinesses_XP1" (
		"HappinessType" TEXT NOT NULL,
		"IdentityPerTurnChange" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(HappinessType),
		FOREIGN KEY (HappinessType) REFERENCES Happinesses(HappinessType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "LoyaltyLevels" (
		"LoyaltyLevelType" TEXT NOT NULL,
		"YieldChange" REAL NOT NULL DEFAULT 0,
		"GrowthChange" REAL NOT NULL DEFAULT 0,
		"Name" TEXT NOT NULL,
		"Description" TEXT,
		"LoyaltyMax" INTEGER NOT NULL DEFAULT 0,
		"LoyaltyMin" INTEGER NOT NULL DEFAULT 0,
		"IdentityChange" REAL NOT NULL DEFAULT 0,
		PRIMARY KEY(LoyaltyLevelType));

CREATE TABLE "Moments" (
		"MomentType" TEXT NOT NULL,
		"Name" LocalizedText NOT NULL,
		"Description" LocalizedText NOT NULL,
		"InstanceDescription" LocalizedText,
		"InterestLevel" INTEGER NOT NULL DEFAULT 0,
		"EraScore" INTEGER,
		"RepeatTurnCooldown" INTEGER,
		"CommemorationType" TEXT,
		"MinimumGameEra" TEXT,
		"MaximumGameEra" TEXT,
		"BackgroundTexture" TEXT,
		"IconTexture" TEXT,
		"MomentIllustrationType" TEXT,
		"ObsoleteEra" TEXT,
		PRIMARY KEY(MomentType),
		FOREIGN KEY (MomentType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CommemorationType) REFERENCES CommemorationTypes(CommemorationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MinimumGameEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MaximumGameEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MomentIllustrationType) REFERENCES MomentIllustrationTypes(MomentIllustrationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ObsoleteEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "MomentDataTypes" (
		"MomentDataType" TEXT NOT NULL,
		"Name" INTEGER,
		PRIMARY KEY(MomentDataType));

CREATE TABLE "MomentIllustrations" (
		"MomentIllustrationType" TEXT NOT NULL,
		"MomentDataType" TEXT NOT NULL,
		"GameDataType" TEXT NOT NULL,
		"Texture" TEXT NOT NULL,
		PRIMARY KEY(MomentIllustrationType, MomentDataType, GameDataType),
		FOREIGN KEY (GameDataType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MomentIllustrationType) REFERENCES MomentIllustrationTypes(MomentIllustrationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MomentDataType) REFERENCES MomentDataTypes(MomentDataType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "MomentIllustrationTypes" (
		"MomentIllustrationType" TEXT NOT NULL UNIQUE,
		PRIMARY KEY(MomentIllustrationType));

CREATE TABLE "Policies_XP1" (
		"PolicyType" TEXT NOT NULL,
		"MinimumGameEra" TEXT,
		"MaximumGameEra" TEXT,
		"RequiresDarkAge" BOOLEAN NOT NULL CHECK (RequiresDarkAge IN (0,1)) DEFAULT 0,
		"RequiresGoldenAge" BOOLEAN NOT NULL CHECK (RequiresGoldenAge IN (0,1)) DEFAULT 0,
		PRIMARY KEY(PolicyType),
		FOREIGN KEY (MinimumGameEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MaximumGameEra) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Projects_XP1" (
		"ProjectType" TEXT NOT NULL,
		"IdentityPerCitizenChange" REAL NOT NULL DEFAULT 0,
		"UnlocksFromEffect" BOOLEAN NOT NULL CHECK (UnlocksFromEffect IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ProjectType),
		FOREIGN KEY (ProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "SecretSocieties" (
		"SecretSocietyType" TEXT NOT NULL,
		"Name" LocalizedText NOT NULL,
		"Description" LocalizedText NOT NULL,
		"DiscoveryText" LocalizedText NOT NULL,
		"MembershipText" LocalizedText NOT NULL,
		"GovernorType" TEXT,
		"DiscoverAtBarbarianCampBaseChance" INTEGER NOT NULL DEFAULT 0,
		"DiscoverAtCityStateBaseChance" INTEGER NOT NULL DEFAULT 0,
		"DiscoverAtGoodyHutBaseChance" INTEGER NOT NULL DEFAULT 0,
		"DiscoverAtNaturalWonderBaseChance" INTEGER NOT NULL DEFAULT 0,
		"SmallIcon" TEXT NOT NULL,
		"IconString" TEXT NOT NULL,
		PRIMARY KEY(SecretSocietyType),
		FOREIGN KEY (GovernorType) REFERENCES Governors(GovernorType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitRetreats_XP1" (
		"UnitRetreatType" TEXT NOT NULL,
		"BuildingType" TEXT,
		"UnitType" TEXT NOT NULL,
		"ImprovementType" TEXT,
		PRIMARY KEY(UnitRetreatType, UnitType));


-- Navigation Properties (if any)
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Alliances", "ActionCollection", "DiplomaticActions", 1,"SELECT T1.rowid from DiplomaticActions as T1 inner join DiplomaticActions_XP1 as T2 on T2.DiplomaticActionType = T1.DiplomaticActionType inner join Alliances as T3 on T3.AllianceType = T2.AllianceType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CommemorationTypes", "CommemorationCollection", "CommemorationModifiers", 1,"SELECT T1.rowid from CommemorationModifiers as T1 inner join CommemorationTypes as T2 on T2.CommemorationType = T1.CommemorationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CommemorationTypes", "ComplimentCollection", "ComplimentModifiers", 1,"SELECT T1.rowid from ComplimentModifiers as T1 inner join CommemorationTypes as T2 on T2.CommemorationType = T1.CommemorationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CommemorationTypes", "MaximumGameEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join CommemorationTypes as T2 on T2.MaximumGameEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CommemorationTypes", "MinimumGameEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join CommemorationTypes as T2 on T2.MinimumGameEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions_XP1", "AllianceReference", "Alliances", 0,"SELECT T1.rowid from Alliances as T1 inner join DiplomaticActions_XP1 as T2 on T2.AllianceType = T1.AllianceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions_XP1", "RequiresGoldenAgeCommemorationTypeReference", "CommemorationTypes", 0,"SELECT T1.rowid from CommemorationTypes as T1 inner join DiplomaticActions_XP1 as T2 on T2.RequiresGoldenAgeCommemorationType = T1.CommemorationType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticVisibilitySources_XP1", "TradePostTraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join DiplomaticVisibilitySources_XP1 as T2 on T2.TradePostTrait = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("EmergencyAlliances", "Effects", "EmergencyBuffs", 1,"SELECT T1.rowid from EmergencyBuffs as T1 inner join EmergencyAlliances as T2 on T2.EmergencyType = T1.EmergencyType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("EmergencyAlliances", "EmergencyTextBlock", "EmergencyTexts", 0,"SELECT T1.rowid from EmergencyTexts as T1 inner join EmergencyAlliances as T2 on T2.EmergencyText = T1.Type where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("EmergencyAlliances", "GoalTextBlock", "EmergencyGoalTexts", 0,"SELECT T1.rowid from EmergencyGoalTexts as T1 inner join EmergencyAlliances as T2 on T2.GoalText = T1.GoalType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("EmergencyAlliances", "Rewards", "EmergencyRewards", 1,"SELECT T1.rowid from EmergencyRewards as T1 inner join EmergencyAlliances as T2 on T2.EmergencyType = T1.EmergencyType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("EmergencyBuffs", "EmergencyRef", "EmergencyAlliances", 0,"SELECT T1.rowid from EmergencyAlliances as T1 inner join EmergencyBuffs as T2 on T2.EmergencyType = T1.EmergencyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Governors", "PromotionCollection", "GovernorPromotions", 1,"SELECT T1.rowid from GovernorPromotions as T1 inner join GovernorPromotionSets as T2 on T2.GovernorPromotion = T1.GovernorPromotionType inner join Governors as T3 on T3.GovernorType = T2.GovernorType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Governors", "SecretSocietyCollection", "SecretSocieties", 1,"SELECT T1.rowid from SecretSocieties as T1 inner join Governors as T2 on T2.GovernorType = T1.GovernorType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GovernorPromotions", "GovernorCollection", "Governors", 1,"SELECT T1.rowid from Governors as T1 inner join GovernorPromotionSets as T2 on T2.GovernorType = T1.GovernorType inner join GovernorPromotions as T3 on T3.GovernorPromotionType = T2.GovernorPromotion where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GovernorPromotions", "PrereqGovernorPromotions", "GovernorPromotions", 1,"SELECT T1.rowid from GovernorPromotions as T1 inner join GovernorPromotionPrereqs as T2 on T2.PrereqGovernorPromotion = T1.GovernorPromotionType inner join GovernorPromotions as T3 on T3.GovernorPromotionType = T2.GovernorPromotionType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GovernorPromotionConditions", "EarliestGameEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join GovernorPromotionConditions as T2 on T2.EarliestGameEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GovernorPromotionModifiers", "GovernorPromotionReference", "GovernorPromotions", 0,"SELECT T1.rowid from GovernorPromotions as T1 inner join GovernorPromotionModifiers as T2 on T2.GovernorPromotionType = T1.GovernorPromotionType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GovernorReplaces", "BaseGovernorReference", "Governors", 0,"SELECT T1.rowid from Governors as T1 inner join GovernorReplaces as T2 on T2.ReplacesGovernorType = T1.GovernorType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GovernorReplaces", "ReplacementGovernorReference", "Governors", 0,"SELECT T1.rowid from Governors as T1 inner join GovernorReplaces as T2 on T2.UniqueGovernorType = T1.GovernorType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Moments", "CommemorationReference", "CommemorationTypes", 0,"SELECT T1.rowid from CommemorationTypes as T1 inner join Moments as T2 on T2.CommemorationType = T1.CommemorationType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Moments", "MaximumGameEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Moments as T2 on T2.MaximumGameEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Moments", "MinimumGameEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Moments as T2 on T2.MinimumGameEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Moments", "ObsoleteEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Moments as T2 on T2.ObsoleteEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Policies_XP1", "MaximumGameEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Policies_XP1 as T2 on T2.MaximumGameEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Policies_XP1", "MinimumGameEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Policies_XP1 as T2 on T2.MinimumGameEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("SecretSocieties", "GovernorReference", "Governors", 0,"SELECT T1.rowid from Governors as T1 inner join SecretSocieties as T2 on T2.GovernorType = T1.GovernorType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
