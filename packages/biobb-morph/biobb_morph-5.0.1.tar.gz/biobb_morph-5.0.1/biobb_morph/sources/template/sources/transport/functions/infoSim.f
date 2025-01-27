C
C Write simulation info to file
      ! OPEN(15,FILE=infoFilePath_T_D, status='old', position='append')

      ! WRITE(15,*) '---------------'
      ! WRITE(15,*) 'SIMULATION INFO'
      ! WRITE(15,*) '---------------'
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'i_numElem = ', i_numElem
      ! WRITE(15,*) 'Current step number: ', KSTEP
      ! WRITE(15,*) 'Current increment number: ', KINC
      ! WRITE(15,*) 'JTYPE = ', JTYPE
      ! WRITE(15,*) 'JELEM = ', JELEM
      ! WRITE(15,*) 'Global SDVs per integ point:', ngSdv
      ! WRITE(15,*) 'Local SDVs per integ point:', nlSdv
      ! WRITE(15,*) 'Le = ', Le
      ! WRITE(15,*) 'NPREDF = ', NPREDF
      ! WRITE(15,*) 'PNEWDT = ', PNEWDT
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'User element subroutine UEL called'
      ! WRITE(15,*) '--------------------------------------------'
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'name of the SET= ', MATNAME
      ! WRITE(15,*) 'NPROPS = ', NPROPS
      ! WRITE(15,*) 'NNODE = ', NNODE
      ! WRITE(15,*) 'MCRD = ', MCRD
      ! WRITE(15,*) 'NDIM = ', NDIM

      ! WRITE(15,*) 'COORDS = ', COORDS
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'PROPS'
      ! WRITE(15,*) '-----'
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'Mechanical properties:'
      ! WRITE(15,*) 'E = ', E
      ! WRITE(15,*) 'NU = ', NU
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'Water diffusivities:'
      ! WRITE(15,*) 'D_WAT(1) O2 = ', D_WAT(1)
      ! WRITE(15,*) 'D_WAT(2) Lac = ', D_WAT(2)
      ! WRITE(15,*) 'D_WAT(3) Gluc = ', D_WAT(3)
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'RHO_0 = ', RHO_0
      ! WRITE(15,*) 'ph_val_0 = ', ph_val
      ! WRITE(15,*) 'CELL_0 = ', CELL
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'Some variables for debugging'
      ! WRITE(15,*) '----------------------------'
      ! WRITE(15,*) ' '
      ! WRITE(15,*) 'NDOFEL = ', NDOFEL
      ! WRITE(15,*) 'NDOFN = ', NDOFN
      ! WRITE(15,*) 'DETDFG = ', DETDFG
      ! WRITE(15,*) 'NF = ', NF
      ! WRITE(15,*) 'R_SOL(1) = ', R_SOL(1)
      ! WRITE(15,*) 'dR_SOL(2) = ', dR_SOL(1)
      ! WRITE(15, *) 'D_SOL(1) = ', D_SOL(1)
      ! WRITE(15, *) 'D_SOL(2) = ', D_SOL(2)
      ! WRITE(15, *) 'D_SOL(3) = ', D_SOL(3)
      ! CLOSE(15)

C Print simulation info to screen

      PRINT *, '--------------------------------------------'
      PRINT *, 'UEL'
      PRINT *, 'MCRD = ', MCRD
      PRINT *, 'NDIM = ', NDIM
      PRINT *, 'i_numElem = ', i_numElem
      PRINT *, 'Current step number: ', KSTEP
      PRINT *, 'Current increment number: ', KINC
      PRINT *, 'CMNAME = ', MATNAME
      PRINT *, 'JTYPE = ', JTYPE
      PRINT *, 'JELEM = ', JELEM
      PRINT *, 'ngSdv = ', ngSdv
      PRINT *, 'nlSdv = ', nlSdv
      PRINT *, 'Le = ', Le
      PRINT *, 'NPREDF = ', NPREDF
      DO I = 1, NPROPS
            PRINT *, 'PROPS(', I, ') = ', PROPS(I)
      ENDDO
      PRINT *, 'NNODE = ', NNODE
      PRINT *, 'NDOFEL = ', NDOFEL
      PRINT *, 'NDOFN = ', NDOFN
      PRINT *, 'NF = ', NF
      PRINT *, 'DETDFG = ', DETDFG
      PRINT *, 'U = ', U
      PRINT *, ' '
      PRINT *, 'O2_CONC: '
      PRINT *, O2_CONC
      PRINT *, 'LACT_CONC: '
      PRINT *, LACT_CONC
      PRINT *, 'GLUC_CONC: '
      PRINT *, GLUC_CONC
      PRINT *, ' '
      PRINT *, 'COORDS: ', COORDS
      PRINT *, ' '
      PRINT *, 'U: ', U
      PRINT *, ' '
      PRINT *, 'COORDSC: ', COORDSC
      PRINT *, ' '
C print the AMATRX
      PRINT *, 'AMATRX: '
      DO I=1,NDOFEL
            PRINT *, I , AMATRX(I,I)
      END DO
C print the RHS
      PRINT *, 'RHS: '
      DO I=1,NDOFEL
            PRINT *, I , RHS(I,NRHS)
      END DO
      PRINT *, 'R_SOL(1)', R_SOL(1)
      PRINT *, 'dR_SOL(1)', dR_SOL(1)
      PRINT *, 'R_SOL(2)', R_SOL(2)
      PRINT *, 'dR_SOL(2)', dR_SOL(2)
      PRINT *, 'R_SOL(3)', R_SOL(3)
      PRINT *, 'dR_SOL(3)', dR_SOL(3)
      PRINT *, ' '

C close the file

