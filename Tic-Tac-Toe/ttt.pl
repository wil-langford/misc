#!/usr/bin/perl -w

# Copyright 2009 Wil Langford

#  This work is licensed under the Creative Commons Attribution-ShareAlike
#  3.0 Unported License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-sa/3.0/.

# This Perl script generates a PDF of the directed graph representation of the
# game tree of Tic-Tac-Toe.  It's not, strictly speaking, the game tree, because
# it has cycles.  All game states up to symmetry are contained in a single
# game state in the output.

# You, uh... you may want a magnifying glass.

# REQUIREMENTS: Perl and an executable copy of "dot" from Graphviz.

use strict;

use constant MAXRANK => 9;
use constant RENDERRANK => 9;
use constant FILEIO => 1;
use constant DEBUGFILEIO => 0;

use constant I => "123456789";
use constant R => "741852963";
use constant F => "147258369";

use constant COLORS => { 'corn' => 'green4',
						 'edge' => 'red4',
						 'cent' => 'blue4'
						 };
use constant STYLES => { 'corn' => 'oldiamond',
						 'edge' => 'olbox',
						 'cent' => 'odot'
						 };

my @colors = (  COLORS->{'corn'}, COLORS->{'edge'}, COLORS->{'corn'}, 
				COLORS->{'edge'}, COLORS->{'cent'}, COLORS->{'edge'}, 
				COLORS->{'corn'}, COLORS->{'edge'}, COLORS->{'corn'}, 
			);
my @styles = (  STYLES->{'corn'}, STYLES->{'edge'}, STYLES->{'corn'}, 
				STYLES->{'edge'}, STYLES->{'cent'}, STYLES->{'edge'}, 
				STYLES->{'corn'}, STYLES->{'edge'}, STYLES->{'corn'}, 
			);

my $leafcount=0;

my %goodhands;  # All game states.  Get it?  You're in
				# "good hands" with "all states?"  HAR!

my @maps = (I, R, Map(R,R), Map(R,R,R), F, Map(F,R), Map(F,R,R), Map(F,R,R,R));

sub Map {
	my @A=split('', shift);
	my ($i, @B, $B);
	foreach(@_){
		my @f=split('',$_);

		for($i=0;$i<=8;$i++){
			$B[$i]=@A[$f[$i]-1];
		}

		@A=@B;
	}

	$B=join('',@B);
	return $B;
}

sub PG {
	print(substr($_[0],0,3)."   state: ".$_[0]."\n");
	print(substr($_[0],3,3)."   moves: \n");
	print(substr($_[0],6,3)."   \n");
}

sub NodeString {
	my $A=$_[0];
	my $B;
	my $C;
	my $score=Score($A);
	my $scorestring='}|{';

	if ($score eq 'X' || $score eq 'O') {
		$scorestring .= $score . ' Wins';
	} elsif ($score eq 'D') {
		$scorestring .= 'Draw';
	} else {
		$scorestring = '';
	}

	$C = $A;
	$C =~ tr/-/u/;

	$A =~ tr/-/ /;

	$B =$C . ' [ label="{';
	$B.=join("|",split('',substr($A,0,3)));
	$B.='}|{';
	$B.=join("|",split('',substr($A,3,3)));
	$B.='}|{';
	$B.=join("|",split('',substr($A,6,3)));
	$B.=$scorestring;
	$B.='}" ]';
	$B.="\n";

	return $B;
}

sub EdgeString {
	my $parent=$_[0];
	my $child=$_[1];
	my $edgestring='';

	my $diff=DiffLoc($parent,$child);
	my $color=$colors[$diff];
	my $style=$styles[$diff];

	$parent =~ tr/-/u/;
	$child =~ tr/-/u/;
	
	$edgestring.=$parent . '->' . $child;
	$edgestring.=" [ ";
	$edgestring.="color=$color";
	$edgestring.=", ";
	$edgestring.="arrowhead=$style";
	$edgestring.=", ";
	$edgestring.="arrowtail=$style";
	$edgestring.=" ]\n";

	return $edgestring;
}

sub Moves {
	my $who;
	my $state=$_[0];
	my $pos=index($state,"-");
	my @mvs;
	my $cs;
	my $compstate;

	$who=(RankState($state) % 2 ==0)?"X":"O";

	POS: while($pos>-1) {
		$cs=$state;

		substr($cs,$pos,1,$who);

		$cs=Equivalize($cs);

		foreach $compstate (@mvs){
			if ($compstate eq $cs) {
				next POS;
			}
		}

		push(@mvs,$cs);

	} continue {
		$pos=index($state,"-",$pos+1);
	}

	return @mvs;
}

sub DiffLoc {
	my $i;
	my $A=Equivalize($_[0]);
	my $B=Equivalize($_[1]);
	my $MA;
	my $diffcount=0;
	my $diffloc=-1;

	SYMMETRY: foreach(@maps){
			$MA=Map($A,$_);
			for ($i=0;$i<length($A);$i++){
				if (substr($MA,$i,1) ne substr($B,$i,1)) {
					$diffcount++;
					$diffloc=$i;
				}
				if ($diffcount>1) {
					$diffcount=0;
					next SYMMETRY;
				}
				last SYMMETRY if ($diffcount==1 and $i==8);
			}
	}

	if ($diffcount==1) {
		return $diffloc;
	} else {
		return -1;
	}

=pod
	while(length($A)>0 and length($B)>0){
		if(not chop($A) eq chop($B)) {
			return length($A);
		}
	}

	return -1;
=cut
}

sub Equiv {
	my $A=$_[0];
	my $B=$_[1];

	return (Equivalize($A) eq Equivalize($B))?1:0;
}

sub Equivs {
	my $A=$_[0];
	my $MA;
	my $extant;
	my @A;
	
	SYMMETRY: foreach(@maps){
			$MA=Map($A,$_);
			foreach (@A){
				next SYMMETRY if ($MA eq $_);
			}
			push(@A,$MA);
	}
	return sort @A;
}

sub Equivalize {
	my $A=$_[0];

	if (not defined($goodhands{$A})){
		foreach(Equivs($A)){
			$goodhands{$_}=$A;
		}
	}


	return $goodhands{$A};
}

sub Score {
	my $A=$_[0];
	my $AF = Map($A,F);
	my $AR = Map($A,R);
	my $player;
	my $winner="-";

	foreach $player ('X','O'){
		if (substr($A,0,3) eq ($player x 3) ||
			substr($A,3,3) eq ($player x 3) ||
			substr($A,6,3) eq ($player x 3) ||
			substr($AF,0,3) eq ($player x 3) ||
			substr($AF,3,3) eq ($player x 3) ||
			substr($AF,6,3) eq ($player x 3) ||
			( substr($A,0,1) eq  $player &&
			  substr($A,4,1) eq  $player &&
			  substr($A,8,1) eq  $player ) ||
			( substr($AR,0,1) eq  $player &&
			  substr($AR,4,1) eq  $player &&
			  substr($AR,8,1) eq  $player )) {
			$winner=$player;
		}
	}

	$winner = ($winner eq "-" && index($A,"-")==-1) ? "D" : $winner;

	return $winner;
}

sub RankState {
	my $A=$_[0];
	my $count;
	my $diffxo;
	$count = ($A =~ tr/-//);
	$diffxo = ($A =~ tr/X//) - ($A =~ tr/O//);

	if($diffxo>1 or $diffxo<0){
		print "\n\nBADNESS: Unbalanced state: $A\n";
		exit;
	}

	return 9-$count;
}

sub buildtree {
	my $i;
	my $rank=0;
	my %rank;
	my $state;
	my %state;
	my $score;
	my $childstate;
	my $children;
	my $compstate;
	my @Tree=(
		{
			"---------" => {
				"Child" => [ Moves("---------") ],
			},
		},
	);


	if(DEBUGFILEIO){
	open(STATES,">states.txt");
	}

#  Iterate over the ranks (0-9)
	for($rank=0;$rank<=MAXRANK;$rank++){

	if(DEBUGFILEIO){
		open(RANK,">rank-$rank");
	}

		# iterate over the states of the rank
		foreach $state (sort keys %{$Tree[$rank]} ){
			if(RankState($state)!=$rank) {
				print "$rank != $state  !!!!!\n";
				exit;
			}
			$state=Equivalize($state);

			# is the current state a leaf?
			$score=Score($state);


			# if it's a leaf and is a win for one of the players...
			if ($score eq "X" || $score eq "O") {
				print "  " x $rank . $state . "   " . $score . " Wins!\n";
				$Tree[$rank]{$state}{"Leaf"}=$score;
				$leafcount++;

			# if it's a leaf and it's a draw...
			} elsif ($score eq "D") {
				print "  " x $rank . $state . "   Draw!\n";
				$Tree[$rank]{$state}{"Leaf"}=$score;
				$leafcount++;
			
			# if it's not a leaf...
			} else {
				print "  " x $rank . $state . "\n";
			}

			# output stuff to files
			if(DEBUGFILEIO){
			print RANK $state . "\n";
			print STATES $state . "\n";
			}

			# iterate over the child states of the current state which 
			# were computed and stored on a previous iteration
			$children=$#{$Tree[$rank]{$state}{"Child"}};

			CHILD: for($i=0;$i<=$#{$Tree[$rank]{$state}{"Child"}};$i++){
				$childstate=$Tree[$rank]{$state}{"Child"}[$i];
				$childstate=Equivalize($childstate);

				$score=Score($childstate);
				if($score ne "-") {
					$Tree[$rank+1]{$childstate}{"Score"} = $score ;
				} else {
					$Tree[$rank+1]{$childstate}{"Child"} = [ Moves($childstate) ];
				}
			}
		}
		close(RANK) if DEBUGFILEIO;
	}

	close(STATES) if DEBUGFILEIO;

	return @Tree;
}

my @Tree;
@Tree = buildtree;

open(DOTFILE,">ttt.dot") if FILEIO;

if(FILEIO) {
print DOTFILE <<HEADER;
digraph gametree {

rankdir=LR

ranksep=50
nodesep=1

node [ shape=record, fontname=Courier ]
HEADER
}

my ($rank,$state,$child);

for($rank=0;$rank<=RENDERRANK+1;$rank++){
	foreach $state (sort keys %{$Tree[$rank]}) {
		print DOTFILE NodeString($state) if FILEIO;
		foreach $child (@{$Tree[$rank]{$state}{"Child"}}) {
			print DOTFILE EdgeString($state,$child) if (FILEIO && $child ne '' && $rank <= RENDERRANK);
		}
	}
}

if(FILEIO){
print DOTFILE <<FOOTER;

}
FOOTER
}

print("There are $leafcount leaves.\n\n");

my $one='uOuuXuuuu';
my $two=Map('uOuuXuuXu',F);

# print("The difference between $one and $two is at location " . DiffLoc($one,$two) . ".\n");

print("\n\nRunning dot on the generated file.\n");

system("dot ttt.dot -Tpdf -o Tic-Tac-Toe-Tree.pdf");

print("\n\n");
