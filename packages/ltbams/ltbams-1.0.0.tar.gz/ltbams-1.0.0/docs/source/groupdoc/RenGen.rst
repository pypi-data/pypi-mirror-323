.. _RenGen:

================================================================================
RenGen
================================================================================
Renewable generator (converter) group.

See ANDES Documentation SynGen here for the notes on replacing StaticGen and setting the power
ratio parameters.

Reference:

[1] ANDES Documentation, RenGen, [Online]

Available:

https://docs.andes.app/en/latest/groupdoc/RenGen.html#rengen

Common Parameters: u, name, idx, bus, gen, Sn, q0

Common Variables: Pe, Qe

Available models:
REGCA1_

.. _REGCA1:

--------------------------------------------------------------------------------
REGCA1
--------------------------------------------------------------------------------
Renewable generator scheduling model.

Reference:

[1] ANDES Documentation, REGCA1

Available:
https://docs.andes.app/en/latest/groupdoc/RenGen.html#regca1

Parameters
----------

+---------+------------------+------------------------------+---------+--------+------------+
|  Name   |      Symbol      |         Description          | Default |  Unit  | Properties |
+=========+==================+==============================+=========+========+============+
|  idx    |                  | unique device idx            |         |        |            |
+---------+------------------+------------------------------+---------+--------+------------+
|  u      | :math:`u`        | connection status            | 1       | *bool* |            |
+---------+------------------+------------------------------+---------+--------+------------+
|  name   |                  | device name                  |         |        |            |
+---------+------------------+------------------------------+---------+--------+------------+
|  bus    |                  | interface bus idx            |         |        | mandatory  |
+---------+------------------+------------------------------+---------+--------+------------+
|  gen    |                  | static generator index       |         |        | mandatory  |
+---------+------------------+------------------------------+---------+--------+------------+
|  Sn     | :math:`S_n`      | device MVA rating            | 100     | *MVA*  |            |
+---------+------------------+------------------------------+---------+--------+------------+
|  gammap | :math:`\gamma_P` | P ratio of linked static gen | 1       |        |            |
+---------+------------------+------------------------------+---------+--------+------------+
|  gammaq | :math:`\gamma_Q` | Q ratio of linked static gen | 1       |        |            |
+---------+------------------+------------------------------+---------+--------+------------+


