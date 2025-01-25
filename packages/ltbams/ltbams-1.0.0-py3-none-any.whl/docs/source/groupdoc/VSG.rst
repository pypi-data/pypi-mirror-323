.. _VSG:

================================================================================
VSG
================================================================================
Renewable generator with virtual synchronous generator (VSG) control group.

Note that this is a group separate from ``RenGen`` for VSG scheduling study.

Common Parameters: u, name, idx, bus, gen, Sn

Common Variables: Pe, Qe

Available models:
REGCV1_,
REGCV2_

.. _REGCV1:

--------------------------------------------------------------------------------
REGCV1
--------------------------------------------------------------------------------
Voltage-controlled converter model (virtual synchronous generator) with
inertia emulation.

Here Mmax and Dmax are assumed to be constant, but they might subject to
the operating condition of the converter.

Notes
-----
- The generation is defined by group :ref:`StaticGen`
- Generation cost is defined by model :ref:`GCost`
- Inertia emulation cost is defined by model :ref:`VSGCost`

Reference:

[1] ANDES Documentation, REGCV1

Available:

https://docs.andes.app/en/latest/groupdoc/RenGen.html#regcv1

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
|  zone   |                  | Retrieved zone idx           |         |        |            |
+---------+------------------+------------------------------+---------+--------+------------+
|  M      | :math:`M`        | Inertia emulation            | 10      | *s*    | power      |
+---------+------------------+------------------------------+---------+--------+------------+
|  D      | :math:`D`        | Damping emulation            | 0       | *p.u.* | power      |
+---------+------------------+------------------------------+---------+--------+------------+
|  Mmax   | :math:`M_{max}`  | Maximum inertia emulation    | 99      | *s*    | power      |
+---------+------------------+------------------------------+---------+--------+------------+
|  Dmax   | :math:`D_{max}`  | Maximum damping emulation    | 99      | *p.u.* | power      |
+---------+------------------+------------------------------+---------+--------+------------+


.. _REGCV2:

--------------------------------------------------------------------------------
REGCV2
--------------------------------------------------------------------------------
Voltage-controlled VSC, identical to :ref:`REGCV1`.

Reference:

[1] ANDES Documentation, REGCV2

Available:

https://docs.andes.app/en/latest/groupdoc/RenGen.html#regcv2

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
|  zone   |                  | Retrieved zone idx           |         |        |            |
+---------+------------------+------------------------------+---------+--------+------------+
|  M      | :math:`M`        | Inertia emulation            | 10      | *s*    | power      |
+---------+------------------+------------------------------+---------+--------+------------+
|  D      | :math:`D`        | Damping emulation            | 0       | *p.u.* | power      |
+---------+------------------+------------------------------+---------+--------+------------+
|  Mmax   | :math:`M_{max}`  | Maximum inertia emulation    | 99      | *s*    | power      |
+---------+------------------+------------------------------+---------+--------+------------+
|  Dmax   | :math:`D_{max}`  | Maximum damping emulation    | 99      | *p.u.* | power      |
+---------+------------------+------------------------------+---------+--------+------------+


