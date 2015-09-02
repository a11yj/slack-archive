#!/usr/local/bin/perl

use strict;
use CGI;
use Storable;
use Cwd;

my $basedir = getcwd;
my $userfile = "$basedir/users";

my $obj = new CGI;

# parameters and contents that will be POSTed by slack
# token=MtdvdIpJjhYfBdtVNbuISBVL
# team_id=T0001
# channel_id=C2147483705
# channel_name=test
# timestamp=1355517523.000005
# user_id=U2147483697
# user_name=Steve
# text=googlebot: What is the air-speed velocity of an unladen swallow?
# trigger_word=googlebot:
my $logfile = $obj->param('channel_name');
$logfile =~s|[^a-zA-Z0-9_-]||g;
my $data = [];
my $log = "$basedir/ch_$logfile";
if ( -f "$log" ) {
			      $data = retrieve("$log");
			     }

push @$data, {
		text => $obj->param('text'),
		user => $obj->param('user_name'),
		time => $obj->param('timestamp')
	       };
store($data, "$log");

my $users = {};
if ( -f "$userfile" ) {
  $users = retrieve("$userfile");
}
$users->{$obj->param('user_id')} = $obj->param('user_name');
store($users, "$userfile");


open(OUT, " >> $basedir/_ch_$logfile.csv");
my $text = $obj->param('text');
$text =~s/"/""/;
print OUT $obj->param('channel_name') . ", " . $obj->param('timestamp') . ", " . $obj->param('user_name') . ', ' . '"' . $text . '"' . "\n";
close(OUT);
print $obj->header(-type => 'text/html;charset=utf-8');
exit;
