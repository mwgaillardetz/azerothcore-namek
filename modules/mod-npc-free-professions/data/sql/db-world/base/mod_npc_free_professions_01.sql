-- --------------------------------------------------------------------------------------
-- Profession NPC
-- --------------------------------------------------------------------------------------
DELETE FROM `creature_template` WHERE (`entry` = 199999);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `IconName`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `ScriptName`, `VerifiedBuild`) VALUES
(199999, 'Kaylub', '|cff00ccffProfessions NPC|r', 'Speak', 80, 80, 35, 1, 1, 1.14286, 'npc_free_professions', NULL);
DELETE FROM `creature_template_model` WHERE (`CreatureID` = 199999);
INSERT INTO `creature_template_model`(`CreatureID`,`Idx`,`CreatureDisplayID`,`DisplayScale`,`Probability`,`VerifiedBuild`) values 
(199999,0,31833,1,1,0);

UPDATE `creature_template` SET `npcflag`=`npcflag`|1, `flags_extra`=`flags_extra`|16777216 WHERE `entry`=199999;
