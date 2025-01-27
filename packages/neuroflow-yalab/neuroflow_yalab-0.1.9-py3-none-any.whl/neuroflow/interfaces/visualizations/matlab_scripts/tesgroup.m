function G=tesgroup(F)
 % function G=tesgroup(F)
 % ------------------------------------------------------------------------
 %
 % This function finds groups in the tesselation defined by F. F may
 % represent patch type faces or for instances node indices for
 % tetrehedrons, hexahedrons. Row entries in F (e.g. tetrahedron vertex
 % indices) which are "connected" (sharing vertex indices with other row
 % entries in F) are grouped together. The output G is a logic matrix of
 % size(F,1) rows and "number of groups" columns. Each column represents a
 % group and ones appear in the column for each face belonging to the group.
 %
 % % %EXAMPLE:
 % clear all; close all; clc;
 %
 %
 % %%Simulating some isosurface data
 % [X,Y,Z]=meshgrid(linspace(-5,5,35));
 % phi=(1+sqrt(5))/2;
 % M=2 - (cos(X + phi*Y) + cos(X - phi*Y) + cos(Y + phi*Z) + cos(Y - phi*Z) + cos(Z - phi*X) + cos(Z + phi*X));
 % M=M./max(M(:));
 % [F,V] = isosurface(X,Y,Z,M,0.1);
 %
 % %%Normal isosurface plot showing seperate patch objects
 % figure;
 % h=patch('faces',F,'vertices',V);
 % set(h,'FaceColor','b','EdgeColor','none','FaceAlpha',0.5);
 % view(3);light; grid on; axis vis3d;
 %
 % %%Iso surface plots showing grouped patch objects
 %
 % G=tesgroup(F); %Logic array for patch groups
 % pcolors=jet(size(G,2));
 % figure;
 % for i=1:1:size(G,2);
 %     hg=patch('faces',F(G(:,i),:),'vertices',V); %Plotting individual group
 %     set(hg,'FaceColor',pcolors(i,:),'EdgeColor','none','FaceAlpha',0.8);
 % end
 % view(3);light; grid on; axis vis3d;
 % colormap(pcolors); colorbar; caxis([0 size(G,2)]);
 %
 % Kevin Mattheus Moerman
 % kevinmoerman@hotmail.com
 % 15/07/2010
  %------------------------------------------------------------------------
 IND_F=(1:1:size(F,1))';
 IND_F_search=IND_F;
 G=false(size(F,1),1);
 v_search=[ ];
 L=ones(size(IND_F));
 done=0;
 num_v_search=[ ];
 group_found=1;
 group_n=0;
 while done==0;
     if group_found==1;
        L=find(IND_F_search>0,1); %next un-grouped triangle
        v_new=F(L,:); v_new=v_new(:);
        v_search=[v_search; v_new]; v_search=unique(v_search(:));  %Growing number of search vertices
        group_found=0;
    else
        L = any(ismember(F,v_search), 2);
        IND_F_search=IND_F_search.*(L==0); %Setting found to zero
        v_new=F(L,:); v_new=v_new(:);
        v_search=[v_search; v_new]; v_search=unique(v_search(:));  %Growing number of search vertices
    end
    if numel(v_search)==num_v_search; %If the group has not grown
        group_found=1;
        group_n=group_n+1;
        G(:,group_n)=L;
        v_search=[ ];
    end
    num_v_search=numel(v_search);
    if all(IND_F_search==0);
        done=1;
        group_found=1;
        group_n=group_n+1;
        if any(G)==0
            G(:,group_n)=L;
        end
        v_search=[ ];
    end
end
