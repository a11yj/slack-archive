#!/usr/local/bin/perl

use strict;
use CGI;
use Storable;
use Cwd;
use YAML::Tiny;

# Reasonable defaults
my $basedir = getcwd;
my $datadir = "$basedir/data";
my $userfile = "$datadir/users";
my $ConfigFile = "$datadir/slack-archive.conf";

my @tokens;
if ( -f $ConfigFile ) {
  my $config = YAML::Tiny->read($ConfigFile);
  @tokens = @{$config->[0]->{tokens}};
}


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

my $token = $obj->param('token');

if ( $token eq '' or grep(/$token/, @tokens) == 0 ) {
  print $obj->header(-status => 403,
		     -type => "text/html");
  print "Error!";
  exit;
}
  
my $logfile = $obj->param('channel_name');
$logfile =~s|[^a-zA-Z0-9_-]||g;
my $data = [];
my $log = "$datadir/ch_$logfile";
if ( -f "$log" ) {
  $data = retrieve("$log");
}

push @$data, {
	      text => scalar($obj->param('text')),
		user => scalar($obj->param('user_name')),
		time => scalar($obj->param('timestamp'))
	     };
store($data, "$log");

my $users = {};
if ( -f "$userfile" ) {
  $users = retrieve("$userfile");
}
$users->{$obj->param('user_id')} = $obj->param('user_name');
store($users, "$userfile");

my $channels = [];
if ( -f "$channelfile" ) {
  $channels = retrieve("$channelfile");
}
my $ch = { id => $obj->param('channel_id'),
name => $obj->param('channel_name'),
updated => time
};
push $channels, $ch;
store($channels, "$channelfile");


open(OUT, " >> $datadir/_ch_$logfile.csv");
my $text = $obj->param('text');
$text =~s/"/""/;
print OUT $obj->param('token') . ", " . $obj->param('channel_name') . ", " . $obj->param('timestamp') . ", " . $obj->param('user_name') . ', ' . '"' . $text . '"' . "\n";
close(OUT);
print $obj->header(-type => 'text/html;charset=utf-8');
exit;
