--
DELETE FROM `playercreateinfo_item` WHERE `race` = 0 AND `class` = 0 AND `itemid` = 51809;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`) VALUES
(0, 0, 51809, 1, 'One Portable Hole for every newly created player');
